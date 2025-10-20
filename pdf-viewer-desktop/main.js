const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const axios = require('axios')
const os = require('os')

let mainWindow

const OLLAMA_URL = 'http://127.0.0.1:11434'

// Determine courses path based on environment
function getCoursesPath() {
  // In development: use relative path
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    return path.join(__dirname, '..', 'courses')
  }
  
  // In production: use absolute path in user's Desktop
  const desktopPath = path.join(os.homedir(), 'Desktop', 'ai-masters-notes', 'courses')
  
  // Check if courses exist at desktop location
  if (fs.existsSync(desktopPath)) {
    return desktopPath
  }
  
  // Fallback: let user select the courses folder
  return null
}

const COURSES_PATH = getCoursesPath()

console.log('=================================')
console.log('AI Masters PDF Viewer Starting...')
console.log('Packaged:', app.isPackaged)
console.log('Courses Path:', COURSES_PATH)
console.log('Courses Exist:', COURSES_PATH ? fs.existsSync(COURSES_PATH) : false)
console.log('=================================')

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1200,
    minHeight: 800,
    backgroundColor: '#000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    },
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 20, y: 20 },
    vibrancy: 'dark',
    visualEffectState: 'active',
    show: false,
    frame: true,
    transparent: false,
    hasShadow: true
  })

  mainWindow.loadFile('renderer/index.html')

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools()
  }
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC Handlers

// Get all courses with their PDFs
ipcMain.handle('get-courses', async () => {
  try {
    // Check if courses path is available
    if (!COURSES_PATH || !fs.existsSync(COURSES_PATH)) {
      console.error('Courses path not found:', COURSES_PATH)
      return []
    }

    const courses = []
    const courseDirs = fs.readdirSync(COURSES_PATH)
      .filter(file => {
        const fullPath = path.join(COURSES_PATH, file)
        return fs.statSync(fullPath).isDirectory() && !file.startsWith('.')
      })

    for (const courseDir of courseDirs) {
      const coursePath = path.join(COURSES_PATH, courseDir)
      const pdfs = []

      // Find PDFs only in /notes directories
      function findPDFs(dir, relativePath = '') {
        const files = fs.readdirSync(dir)
        
        for (const file of files) {
          const fullPath = path.join(dir, file)
          const relPath = path.join(relativePath, file)
          const stat = fs.statSync(fullPath)

          if (stat.isDirectory() && !file.startsWith('.')) {
            findPDFs(fullPath, relPath)
          } else if (file.toLowerCase().endsWith('.pdf') && relativePath.includes('notes')) {
            // Only include PDFs from /notes directories
            pdfs.push({
              name: file.replace('.pdf', ''),
              path: relPath,
              fullPath: fullPath,
              type: 'notes'
            })
          }
        }
      }

      findPDFs(coursePath)

      courses.push({
        id: courseDir,
        name: courseDir.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        path: coursePath,
        pdfs: pdfs.sort((a, b) => {
          if (a.type === 'notes' && b.type !== 'notes') return -1
          if (a.type !== 'notes' && b.type === 'notes') return 1
          return a.name.localeCompare(b.name)
        })
      })
    }

    return courses.sort((a, b) => a.name.localeCompare(b.name))
  } catch (error) {
    console.error('Error getting courses:', error)
    return []
  }
})

// Get PDF file path
ipcMain.handle('get-pdf-path', async (event, pdfFullPath) => {
  return pdfFullPath
})

// Check if PDF exists
ipcMain.handle('check-pdf-exists', async (event, pdfPath) => {
  return fs.existsSync(pdfPath)
})

// Ollama API calls
ipcMain.handle('ollama-chat', async (event, model, messages) => {
  try {
    console.log('Sending chat request to Ollama with model:', model)
    const response = await axios.post(`${OLLAMA_URL}/api/chat`, {
      model: model,
      messages: messages,
      stream: false
    }, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    return { success: true, data: response.data }
  } catch (error) {
    console.error('Error in Ollama chat:', error.message)
    return { success: false, error: error.message }
  }
})

ipcMain.handle('ollama-chat-stream', async (event, model, messages) => {
  try {
    console.log('Starting stream chat with model:', model)
    const response = await axios.post(`${OLLAMA_URL}/api/chat`, {
      model: model,
      messages: messages,
      stream: true
    }, {
      responseType: 'stream',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    let fullResponse = ''
    
    response.data.on('data', (chunk) => {
      const lines = chunk.toString().split('\n').filter(line => line.trim())
      
      for (const line of lines) {
        try {
          const json = JSON.parse(line)
          if (json.message?.content) {
            fullResponse += json.message.content
            event.sender.send('ollama-stream-data', fullResponse)
          }
        } catch (e) {
          console.error('Error parsing stream:', e)
        }
      }
    })

    return new Promise((resolve) => {
      response.data.on('end', () => {
        event.sender.send('ollama-stream-end')
        resolve({ success: true, data: fullResponse })
      })

      response.data.on('error', (error) => {
        resolve({ success: false, error: error.message })
      })
    })
  } catch (error) {
    return { success: false, error: error.message }
  }
})

ipcMain.handle('ollama-list-models', async () => {
  try {
    console.log('Attempting to connect to Ollama at:', OLLAMA_URL)
    const response = await axios.get(`${OLLAMA_URL}/api/tags`, {
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    console.log('Ollama models fetched successfully:', response.data.models?.length || 0)
    return { success: true, models: response.data.models || [] }
  } catch (error) {
    console.error('Error fetching Ollama models:', error.message)
    console.error('Error details:', error.code, error.response?.status)
    return { success: false, error: error.message, models: [] }
  }
})

// Dialog for selecting PDF files
ipcMain.handle('select-pdf-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'PDF Files', extensions: ['pdf'] }]
  })

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})
