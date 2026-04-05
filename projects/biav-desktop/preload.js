const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to renderer via contextBridge
contextBridge.exposeInMainWorld('biavDesktop', {
  // ===== Platform Info =====
  platform: process.platform,
  isDesktop: true,

  // ===== Window Controls (Windows/Linux custom title bar) =====
  windowMinimize: () => ipcRenderer.send('window-minimize'),
  windowMaximize: () => ipcRenderer.send('window-maximize'),
  windowClose: () => ipcRenderer.send('window-close'),
  windowIsMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  windowIsFullscreen: () => ipcRenderer.invoke('window-is-fullscreen'),

  // ===== File Operations =====
  saveFile: (data, filename, filters) =>
    ipcRenderer.invoke('save-file', { data, filename, filters }),
  openFile: (filters) =>
    ipcRenderer.invoke('open-file', { filters }),

  // ===== App Info =====
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),

  // ===== Theme =====
  getSystemTheme: () => ipcRenderer.invoke('get-system-theme'),

  // ===== Event Listeners =====
  onShortcut: (callback) => {
    const handler = (_, action) => callback(action);
    ipcRenderer.on('shortcut', handler);
    return () => ipcRenderer.removeListener('shortcut', handler);
  },
  onSystemThemeChanged: (callback) => {
    const handler = (_, theme) => callback(theme);
    ipcRenderer.on('system-theme-changed', handler);
    return () => ipcRenderer.removeListener('system-theme-changed', handler);
  },
  onWindowMaximized: (callback) => {
    const handler = (_, isMaximized) => callback(isMaximized);
    ipcRenderer.on('window-maximized', handler);
    return () => ipcRenderer.removeListener('window-maximized', handler);
  },
});
