// Initialize Lucide icons
lucide.createIcons()

// State
let currentCourse = null
let currentPdf = null
let pdfDoc = null
let currentPage = 1
let scale = 1.0
let messages = []
let currentModel = 'llama2'
let isLoadingMessage = false

// PDF.js worker setup
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'

// DOM Elements
const courseListView = document.getElementById('courseListView')
const pdfViewerView = document.getElementById('pdfViewerView')
const courseGrid = document.getElementById('courseGrid')
const pdfCanvas = document.getElementById('pdfCanvas')
const chatMessages = document.getElementById('chatMessages')
const chatInput = document.getElementById('chatInput')
const chatForm = document.getElementById('chatForm')
const modelSelect = document.getElementById('modelSelect')
const splashScreen = document.getElementById('splashScreen')
const pdfLoadingOverlay = document.getElementById('pdfLoadingOverlay')

// Show/hide loading overlay
function showPdfLoading() {
  pdfLoadingOverlay.classList.remove('hidden')
}

function hidePdfLoading() {
  pdfLoadingOverlay.classList.add('hidden')
}

// Hide splash screen
function hideSplash() {
  setTimeout(() => {
    splashScreen.style.display = 'none'
  }, 2500)
}

// Initialize app
async function init() {
  await loadCourses()
  await loadModels()
  setupEventListeners()
  hideSplash()
}

// Load all courses
async function loadCourses() {
  const courses = await window.electronAPI.getCourses()
  
  courseGrid.innerHTML = ''
  
  courses.forEach(course => {
    const card = createCourseCard(course)
    courseGrid.appendChild(card)
  })
}

// Create course card
function createCourseCard(course) {
  const card = document.createElement('div')
  card.className = 'course-card'
  
  const header = document.createElement('div')
  header.className = 'course-header'
  
  const icon = document.createElement('div')
  icon.className = 'course-icon'
  icon.innerHTML = '<i data-lucide="book-open"></i>'
  
  const titleDiv = document.createElement('div')
  titleDiv.className = 'course-title'
  titleDiv.innerHTML = `
    <h3>${course.name}</h3>
    <p class="course-count">${course.pdfs.length} document${course.pdfs.length !== 1 ? 's' : ''}</p>
  `
  
  header.appendChild(icon)
  header.appendChild(titleDiv)
  card.appendChild(header)
  
  if (course.pdfs.length > 0) {
    const pdfList = document.createElement('div')
    pdfList.className = 'pdf-list'
    
    course.pdfs.forEach(pdf => {
      const pdfItem = document.createElement('div')
      pdfItem.className = 'pdf-item'
      
      pdfItem.innerHTML = `
        <div class="pdf-info">
          <i data-lucide="${pdf.type === 'notes' ? 'file-text' : 'presentation'}" class="pdf-icon"></i>
          <div>
            <div class="pdf-name">${pdf.name}</div>
            <div class="pdf-type">${pdf.type}</div>
          </div>
        </div>
        <i data-lucide="chevron-right"></i>
      `
      
      pdfItem.addEventListener('click', () => openPdf(course, pdf))
      pdfList.appendChild(pdfItem)
    })
    
    card.appendChild(pdfList)
  } else {
    const emptyMsg = document.createElement('p')
    emptyMsg.style.color = '#6b7280'
    emptyMsg.style.fontSize = '14px'
    emptyMsg.style.fontStyle = 'italic'
    emptyMsg.textContent = 'No PDFs available for this course yet'
    card.appendChild(emptyMsg)
  }
  
  lucide.createIcons()
  return card
}

// Open PDF
async function openPdf(course, pdf) {
  currentCourse = course
  currentPdf = pdf
  messages = []
  
  // Show loading overlay
  showPdfLoading()
  
  // Update UI
  document.getElementById('courseName').textContent = course.name
  document.getElementById('pdfName').textContent = pdf.name
  document.getElementById('chatCourseName').textContent = course.name
  
  // Switch views with animation
  courseListView.classList.add('hidden')
  pdfViewerView.classList.remove('hidden')
  
  // Load PDF
  await loadPdf(pdf.fullPath)
  
  // Hide loading overlay after PDF is loaded
  setTimeout(() => {
    hidePdfLoading()
  }, 500)
  
  // Clear chat
  chatMessages.innerHTML = `
    <div class="chat-welcome">
      <i data-lucide="bot" class="welcome-icon"></i>
      <p><strong>Ask me anything about this course!</strong></p>
      <p class="welcome-subtitle">I can help with explanations, problem solving, and concept clarification.</p>
    </div>
  `
  lucide.createIcons()
}

// Load PDF document
async function loadPdf(pdfPath) {
  try {
    const loadingTask = pdfjsLib.getDocument(pdfPath)
    pdfDoc = await loadingTask.promise
    currentPage = 1
    scale = 1.0
    
    await renderPage(currentPage)
    updatePageInfo()
    await loadTableOfContents()
  } catch (error) {
    console.error('Error loading PDF:', error)
    alert('Failed to load PDF. Please check the file path.')
  }
}

// Load table of contents
async function loadTableOfContents() {
  const tocList = document.getElementById('tocList')
  tocList.innerHTML = '<p class="toc-empty">Loading table of contents...</p>'
  
  try {
    const outline = await pdfDoc.getOutline()
    
    if (!outline || outline.length === 0) {
      tocList.innerHTML = '<p class="toc-empty">No table of contents available</p>'
      return
    }
    
    tocList.innerHTML = ''
    
    async function renderOutlineItem(item, level = 1) {
      const tocItem = document.createElement('div')
      tocItem.className = 'toc-item'
      tocItem.setAttribute('data-level', level)
      
      // Get destination page
      let pageIndex = null
      if (item.dest) {
        try {
          const dest = typeof item.dest === 'string' ? 
            await pdfDoc.getDestination(item.dest) : item.dest
          if (dest) {
            const ref = dest[0]
            pageIndex = await pdfDoc.getPageIndex(ref)
          }
        } catch (e) {
          console.warn('Could not get page for TOC item:', e)
        }
      }
      
      tocItem.innerHTML = `
        <div class="toc-item-title">${item.title}</div>
        ${pageIndex !== null ? `<div class="toc-item-page">Page ${pageIndex + 1}</div>` : ''}
      `
      
      if (pageIndex !== null) {
        tocItem.addEventListener('click', async () => {
          currentPage = pageIndex + 1
          await renderPage(currentPage)
          updatePageInfo()
          // Auto-hide TOC on mobile
          if (window.innerWidth < 1200) {
            document.getElementById('tocSidebar').classList.add('hidden')
          }
        })
      }
      
      tocList.appendChild(tocItem)
      
      // Render child items
      if (item.items && item.items.length > 0) {
        for (const child of item.items) {
          await renderOutlineItem(child, level + 1)
        }
      }
    }
    
    for (const item of outline) {
      await renderOutlineItem(item)
    }
    
    lucide.createIcons()
  } catch (error) {
    console.error('Error loading table of contents:', error)
    tocList.innerHTML = '<p class="toc-empty">Error loading table of contents</p>'
  }
}

// Render PDF page
async function renderPage(pageNum) {
  if (!pdfDoc) return
  
  const page = await pdfDoc.getPage(pageNum)
  const viewport = page.getViewport({ scale: scale })
  
  const canvas = pdfCanvas
  const context = canvas.getContext('2d')
  
  // Fix for Retina displays - scale canvas for device pixel ratio
  const devicePixelRatio = window.devicePixelRatio || 1
  const scaledViewport = page.getViewport({ scale: scale * devicePixelRatio })
  
  canvas.height = scaledViewport.height
  canvas.width = scaledViewport.width
  canvas.style.height = viewport.height + 'px'
  canvas.style.width = viewport.width + 'px'
  
  const renderContext = {
    canvasContext: context,
    viewport: scaledViewport
  }
  
  await page.render(renderContext).promise
}

// Update page info
function updatePageInfo() {
  if (!pdfDoc) return
  
  document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${pdfDoc.numPages}`
  document.getElementById('zoomInfo').textContent = `${Math.round(scale * 100)}%`
  
  document.getElementById('prevPageBtn').disabled = currentPage <= 1
  document.getElementById('nextPageBtn').disabled = currentPage >= pdfDoc.numPages
  
  // Update page search input max
  document.getElementById('pageSearchInput').setAttribute('max', pdfDoc.numPages)
}

// Load Ollama models
async function loadModels() {
  const result = await window.electronAPI.ollamaListModels()
  
  if (result.success && result.models.length > 0) {
    modelSelect.innerHTML = ''
    result.models.forEach(model => {
      const option = document.createElement('option')
      option.value = model.name
      option.textContent = model.name
      modelSelect.appendChild(option)
    })
    currentModel = result.models[0].name
  } else {
    modelSelect.innerHTML = '<option>No models available</option>'
  }
}

// Send chat message
async function sendMessage(userMessage) {
  if (isLoadingMessage) return
  
  // Add user message
  messages.push({ role: 'user', content: userMessage })
  appendMessage('user', userMessage)
  
  // Show loading
  isLoadingMessage = true
  const loadingId = appendLoadingMessage()
  
  // Prepare messages with context
  const contextMessage = {
    role: 'system',
    content: `You are a helpful AI assistant specialized in academic subjects. The user is currently viewing a PDF document titled "${currentPdf.name}" from the course "${currentCourse.name}". Help them understand the content, answer questions, solve problems, and explain theorems and concepts from this course material. Be concise but thorough in your explanations.`
  }
  
  const fullMessages = [contextMessage, ...messages]
  
  // Stream response
  let assistantResponse = ''
  let responseMessageId = null
  
  window.electronAPI.onOllamaStreamData((data) => {
    assistantResponse = data
    
    if (responseMessageId) {
      updateMessage(responseMessageId, assistantResponse)
    } else {
      removeLoadingMessage(loadingId)
      responseMessageId = appendMessage('assistant', assistantResponse)
    }
  })
  
  window.electronAPI.onOllamaStreamEnd(() => {
    messages.push({ role: 'assistant', content: assistantResponse })
    isLoadingMessage = false
    window.electronAPI.removeOllamaStreamListeners()
  })
  
  const result = await window.electronAPI.ollamaChatStream(currentModel, fullMessages)
  
  if (!result.success) {
    removeLoadingMessage(loadingId)
    appendMessage('assistant', '⚠️ Error: Unable to connect to Ollama. Please make sure Ollama is running locally (ollama serve).')
    isLoadingMessage = false
  }
}

// Append message to chat
function appendMessage(role, content) {
  const messageId = Date.now()
  const messageDiv = document.createElement('div')
  messageDiv.className = `message ${role}`
  messageDiv.dataset.id = messageId
  
  const avatar = document.createElement('div')
  avatar.className = 'message-avatar'
  avatar.innerHTML = role === 'user' 
    ? '<i data-lucide="user"></i>' 
    : '<i data-lucide="bot"></i>'
  
  const contentDiv = document.createElement('div')
  contentDiv.className = 'message-content'
  contentDiv.textContent = content
  
  messageDiv.appendChild(avatar)
  messageDiv.appendChild(contentDiv)
  
  chatMessages.appendChild(messageDiv)
  lucide.createIcons()
  chatMessages.scrollTop = chatMessages.scrollHeight
  
  return messageId
}

// Update existing message
function updateMessage(messageId, content) {
  const messageDiv = chatMessages.querySelector(`[data-id="${messageId}"]`)
  if (messageDiv) {
    const contentDiv = messageDiv.querySelector('.message-content')
    contentDiv.textContent = content
    chatMessages.scrollTop = chatMessages.scrollHeight
  }
}

// Append loading message
function appendLoadingMessage() {
  const loadingId = Date.now()
  const messageDiv = document.createElement('div')
  messageDiv.className = 'message assistant'
  messageDiv.dataset.id = loadingId
  
  const avatar = document.createElement('div')
  avatar.className = 'message-avatar'
  avatar.innerHTML = '<i data-lucide="bot"></i>'
  
  const loadingDiv = document.createElement('div')
  loadingDiv.className = 'message-content'
  loadingDiv.innerHTML = `
    <div class="message-loading">
      <div class="loading-dot"></div>
      <div class="loading-dot"></div>
      <div class="loading-dot"></div>
    </div>
  `
  
  messageDiv.appendChild(avatar)
  messageDiv.appendChild(loadingDiv)
  
  chatMessages.appendChild(messageDiv)
  lucide.createIcons()
  chatMessages.scrollTop = chatMessages.scrollHeight
  
  return loadingId
}

// Remove loading message
function removeLoadingMessage(loadingId) {
  const messageDiv = chatMessages.querySelector(`[data-id="${loadingId}"]`)
  if (messageDiv) {
    messageDiv.remove()
  }
}

// Setup event listeners
function setupEventListeners() {
  // Back button
  document.getElementById('backBtn').addEventListener('click', () => {
    pdfViewerView.classList.add('hidden')
    courseListView.classList.remove('hidden')
    currentCourse = null
    currentPdf = null
    pdfDoc = null
  })
  
  // Toggle chat
  function toggleChat() {
    const chatContainer = document.querySelector('.chat-container')
    const floatingBtn = document.getElementById('floatingChatBtn')
    const btnText = document.getElementById('chatBtnText')
    
    if (chatContainer.classList.contains('hidden')) {
      chatContainer.classList.remove('hidden')
      floatingBtn.classList.add('hidden')
      btnText.textContent = 'Hide Chat'
    } else {
      chatContainer.classList.add('hidden')
      floatingBtn.classList.remove('hidden')
      btnText.textContent = 'Show Chat'
    }
    lucide.createIcons()
  }

  document.getElementById('toggleChatBtn').addEventListener('click', toggleChat)
  document.getElementById('floatingChatBtn').addEventListener('click', toggleChat)
  
  // PDF controls
  document.getElementById('prevPageBtn').addEventListener('click', async () => {
    if (currentPage > 1) {
      currentPage--
      await renderPage(currentPage)
      updatePageInfo()
    }
  })
  
  document.getElementById('nextPageBtn').addEventListener('click', async () => {
    if (currentPage < pdfDoc.numPages) {
      currentPage++
      await renderPage(currentPage)
      updatePageInfo()
    }
  })
  
  document.getElementById('zoomOutBtn').addEventListener('click', async () => {
    if (scale > 0.5) {
      scale = Math.max(0.5, scale - 0.2)
      await renderPage(currentPage)
      updatePageInfo()
    }
  })
  
  document.getElementById('zoomInBtn').addEventListener('click', async () => {
    if (scale < 3.0) {
      scale = Math.min(3.0, scale + 0.2)
      await renderPage(currentPage)
      updatePageInfo()
    }
  })
  
  // Chat settings
  document.getElementById('chatSettingsBtn').addEventListener('click', () => {
    const settings = document.getElementById('chatSettings')
    settings.classList.toggle('hidden')
  })
  
  modelSelect.addEventListener('change', (e) => {
    currentModel = e.target.value
  })
  
  // Page search
  document.getElementById('pageSearchInput').addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
      const pageNum = parseInt(e.target.value)
      if (pageNum && pageNum >= 1 && pageNum <= pdfDoc?.numPages) {
        currentPage = pageNum
        await renderPage(currentPage)
        updatePageInfo()
        e.target.value = ''
      }
    }
  })

  // TOC Toggle
  document.getElementById('toggleTocBtn').addEventListener('click', () => {
    const tocSidebar = document.getElementById('tocSidebar')
    tocSidebar.classList.toggle('hidden')
    lucide.createIcons()
  })

  document.getElementById('closeTocBtn').addEventListener('click', () => {
    document.getElementById('tocSidebar').classList.add('hidden')
  })

  // Chat form
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    
    const message = chatInput.value.trim()
    if (message && !isLoadingMessage) {
      chatInput.value = ''
      await sendMessage(message)
    }
  })
  
  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (!pdfViewerView.classList.contains('hidden') && pdfDoc) {
      // Arrow keys for navigation
      if (e.key === 'ArrowLeft' && currentPage > 1) {
        document.getElementById('prevPageBtn').click()
      } else if (e.key === 'ArrowRight' && currentPage < pdfDoc.numPages) {
        document.getElementById('nextPageBtn').click()
      }
      // +/- for zoom
      else if (e.key === '+' || e.key === '=') {
        document.getElementById('zoomInBtn').click()
      } else if (e.key === '-') {
        document.getElementById('zoomOutBtn').click()
      }
    }
  })
}

// Start the app
init()
