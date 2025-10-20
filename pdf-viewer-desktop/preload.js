const { contextBridge, ipcRenderer } = require('electron')

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Course and PDF operations
  getCourses: () => ipcRenderer.invoke('get-courses'),
  getPdfPath: (pdfFullPath) => ipcRenderer.invoke('get-pdf-path', pdfFullPath),
  checkPdfExists: (pdfPath) => ipcRenderer.invoke('check-pdf-exists', pdfPath),
  selectPdfFile: () => ipcRenderer.invoke('select-pdf-file'),

  // Ollama operations
  ollamaChat: (model, messages) => ipcRenderer.invoke('ollama-chat', model, messages),
  ollamaChatStream: (model, messages) => ipcRenderer.invoke('ollama-chat-stream', model, messages),
  ollamaListModels: () => ipcRenderer.invoke('ollama-list-models'),

  // Stream event listeners
  onOllamaStreamData: (callback) => {
    ipcRenderer.on('ollama-stream-data', (event, data) => callback(data))
  },
  onOllamaStreamEnd: (callback) => {
    ipcRenderer.on('ollama-stream-end', () => callback())
  },
  removeOllamaStreamListeners: () => {
    ipcRenderer.removeAllListeners('ollama-stream-data')
    ipcRenderer.removeAllListeners('ollama-stream-end')
  }
})
