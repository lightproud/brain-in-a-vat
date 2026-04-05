const { app, BrowserWindow, ipcMain, Menu, Tray, shell, dialog, globalShortcut, nativeTheme, session } = require('electron');
const path = require('path');
const fs = require('fs');

// ===== Constants =====
const APP_NAME = '缸中之脑';
const APP_VERSION = '1.0.0';
const IS_MAC = process.platform === 'darwin';
const IS_DEV = process.argv.includes('--dev');

let mainWindow = null;
let tray = null;

// ===== Window State Persistence =====
const STATE_FILE = path.join(app.getPath('userData'), 'window-state.json');

function loadWindowState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { width: 1280, height: 820, x: undefined, y: undefined, isMaximized: false };
  }
}

function saveWindowState() {
  if (!mainWindow) return;
  const bounds = mainWindow.getBounds();
  const state = {
    width: bounds.width,
    height: bounds.height,
    x: bounds.x,
    y: bounds.y,
    isMaximized: mainWindow.isMaximized(),
  };
  try { fs.writeFileSync(STATE_FILE, JSON.stringify(state)); } catch {}
}

// ===== Create Main Window =====
function createWindow() {
  const state = loadWindowState();

  mainWindow = new BrowserWindow({
    width: state.width,
    height: state.height,
    x: state.x,
    y: state.y,
    minWidth: 800,
    minHeight: 600,
    title: APP_NAME,
    titleBarStyle: IS_MAC ? 'hiddenInset' : 'default',
    // Custom frameless on Windows/Linux for sleek look
    frame: IS_MAC,
    backgroundColor: '#0a0b10',
    show: false, // Show after ready-to-show to avoid flash
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      webSecurity: true,
      spellcheck: true,
    },
    icon: getIconPath(),
  });

  if (state.isMaximized) {
    mainWindow.maximize();
  }

  // Load the renderer HTML
  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // Show window when ready (avoids white flash)
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (IS_DEV) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Save state on resize/move
  mainWindow.on('resize', saveWindowState);
  mainWindow.on('move', saveWindowState);
  mainWindow.on('close', saveWindowState);

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Inject desktop-specific CSS after page load
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.insertCSS(getDesktopCSS());
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ===== Anthropic API Proxy =====
// Remove the need for 'anthropic-dangerous-direct-browser-access'
// by handling CORS in the main process
function setupAPIProxy() {
  const filter = { urls: ['https://api.anthropic.com/*'] };

  session.defaultSession.webRequest.onBeforeSendHeaders(filter, (details, callback) => {
    // Remove the dangerous-direct-browser-access header
    delete details.requestHeaders['anthropic-dangerous-direct-browser-access'];
    // Ensure proper origin
    details.requestHeaders['Origin'] = 'https://api.anthropic.com';
    callback({ requestHeaders: details.requestHeaders });
  });

  session.defaultSession.webRequest.onHeadersReceived(filter, (details, callback) => {
    // Allow CORS for Anthropic API
    const headers = details.responseHeaders || {};
    headers['access-control-allow-origin'] = ['*'];
    headers['access-control-allow-headers'] = ['*'];
    headers['access-control-allow-methods'] = ['*'];
    callback({ responseHeaders: headers });
  });
}

// ===== System Tray =====
function createTray() {
  // Use a simple tray icon
  const iconPath = getIconPath();
  if (!iconPath) return;

  tray = new Tray(iconPath);
  tray.setToolTip(APP_NAME);

  const contextMenu = Menu.buildFromTemplate([
    { label: '显示主窗口', click: () => { if (mainWindow) mainWindow.show(); } },
    { type: 'separator' },
    { label: '新对话', accelerator: 'CmdOrCtrl+N', click: () => sendToRenderer('shortcut', 'new-chat') },
    { label: '搜索', accelerator: 'CmdOrCtrl+K', click: () => sendToRenderer('shortcut', 'search') },
    { type: 'separator' },
    { label: '退出', click: () => { app.isQuitting = true; app.quit(); } },
  ]);

  tray.setContextMenu(contextMenu);
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.focus();
      } else {
        mainWindow.show();
      }
    }
  });
}

// ===== Application Menu =====
function createMenu() {
  const template = [
    ...(IS_MAC ? [{
      label: APP_NAME,
      submenu: [
        { label: `关于 ${APP_NAME}`, click: showAbout },
        { type: 'separator' },
        { label: '设置…', accelerator: 'CmdOrCtrl+,', click: () => sendToRenderer('shortcut', 'settings') },
        { type: 'separator' },
        { label: `隐藏 ${APP_NAME}`, role: 'hide' },
        { label: '隐藏其他', role: 'hideOthers' },
        { label: '全部显示', role: 'unhide' },
        { type: 'separator' },
        { label: `退出 ${APP_NAME}`, role: 'quit' },
      ],
    }] : []),
    {
      label: '文件',
      submenu: [
        { label: '新对话', accelerator: 'CmdOrCtrl+N', click: () => sendToRenderer('shortcut', 'new-chat') },
        { type: 'separator' },
        { label: '导出对话…', accelerator: 'CmdOrCtrl+Shift+E', click: () => sendToRenderer('shortcut', 'export') },
        { type: 'separator' },
        ...(IS_MAC ? [] : [
          { label: '设置', accelerator: 'CmdOrCtrl+,', click: () => sendToRenderer('shortcut', 'settings') },
          { type: 'separator' },
          { label: '退出', role: 'quit' },
        ]),
      ],
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销' },
        { role: 'redo', label: '重做' },
        { type: 'separator' },
        { role: 'cut', label: '剪切' },
        { role: 'copy', label: '复制' },
        { role: 'paste', label: '粘贴' },
        { role: 'selectAll', label: '全选' },
        { type: 'separator' },
        { label: '搜索对话', accelerator: 'CmdOrCtrl+K', click: () => sendToRenderer('shortcut', 'search') },
      ],
    },
    {
      label: '视图',
      submenu: [
        { label: '切换侧边栏', accelerator: 'CmdOrCtrl+B', click: () => sendToRenderer('shortcut', 'toggle-sidebar') },
        { label: '切换主题', accelerator: 'CmdOrCtrl+D', click: () => sendToRenderer('shortcut', 'toggle-theme') },
        { type: 'separator' },
        { role: 'zoomIn', label: '放大', accelerator: 'CmdOrCtrl+=' },
        { role: 'zoomOut', label: '缩小' },
        { role: 'resetZoom', label: '重置缩放' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: '全屏' },
        ...(IS_DEV ? [{ type: 'separator' }, { role: 'toggleDevTools', label: '开发者工具' }] : []),
      ],
    },
    {
      label: '窗口',
      submenu: [
        { role: 'minimize', label: '最小化' },
        { label: '最大化', click: () => { if (mainWindow) mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize(); } },
        ...(IS_MAC ? [{ role: 'close', label: '关闭' }] : []),
      ],
    },
    {
      label: '帮助',
      submenu: [
        { label: `关于 ${APP_NAME}`, click: showAbout },
        { type: 'separator' },
        { label: 'GitHub 仓库', click: () => shell.openExternal('https://github.com/lightproud/brain-in-a-vat') },
        { label: '忘却前夜 Steam', click: () => shell.openExternal('https://store.steampowered.com/app/3052450/Morimens/') },
      ],
    },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// ===== IPC Handlers =====
function setupIPC() {
  // Window controls (for custom title bar on Windows/Linux)
  ipcMain.on('window-minimize', () => mainWindow?.minimize());
  ipcMain.on('window-maximize', () => {
    if (mainWindow?.isMaximized()) mainWindow.unmaximize();
    else mainWindow?.maximize();
  });
  ipcMain.on('window-close', () => mainWindow?.close());

  // Window state queries
  ipcMain.handle('window-is-maximized', () => mainWindow?.isMaximized() ?? false);
  ipcMain.handle('window-is-fullscreen', () => mainWindow?.isFullScreen() ?? false);

  // File operations
  ipcMain.handle('save-file', async (_, { data, filename, filters }) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: filename,
      filters: filters || [{ name: 'All Files', extensions: ['*'] }],
    });
    if (result.canceled) return null;
    fs.writeFileSync(result.filePath, Buffer.from(data));
    return result.filePath;
  });

  ipcMain.handle('open-file', async (_, { filters }) => {
    const result = await dialog.showOpenDialog(mainWindow, {
      filters: filters || [{ name: 'All Files', extensions: ['*'] }],
      properties: ['openFile'],
    });
    if (result.canceled) return null;
    const filePath = result.filePaths[0];
    const buffer = fs.readFileSync(filePath);
    return { path: filePath, name: path.basename(filePath), data: buffer.toString('base64') };
  });

  // App info
  ipcMain.handle('get-app-info', () => ({
    version: APP_VERSION,
    platform: process.platform,
    arch: process.arch,
    electronVersion: process.versions.electron,
    userDataPath: app.getPath('userData'),
  }));

  // Theme
  ipcMain.handle('get-system-theme', () => nativeTheme.shouldUseDarkColors ? 'dark' : 'light');

  nativeTheme.on('updated', () => {
    const theme = nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
    mainWindow?.webContents.send('system-theme-changed', theme);
  });

  // Maximized state change notification
  mainWindow?.on('maximize', () => mainWindow?.webContents.send('window-maximized', true));
  mainWindow?.on('unmaximize', () => mainWindow?.webContents.send('window-maximized', false));
}

// ===== Helpers =====
function sendToRenderer(channel, ...args) {
  mainWindow?.webContents.send(channel, ...args);
}

function showAbout() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: `关于 ${APP_NAME}`,
    message: APP_NAME,
    detail: [
      `银芯系统桌面版 v${APP_VERSION}`,
      '',
      'B.I.A.V. Studio AI 增强终端',
      '忘却前夜（Morimens）项目配套工具',
      '',
      `Electron ${process.versions.electron}`,
      `Chrome ${process.versions.chrome}`,
      `Node.js ${process.versions.node}`,
    ].join('\n'),
  });
}

function getIconPath() {
  const iconDir = path.join(__dirname, 'assets');
  if (IS_MAC) {
    const p = path.join(iconDir, 'icon.icns');
    return fs.existsSync(p) ? p : null;
  }
  const p = path.join(iconDir, 'icon.png');
  return fs.existsSync(p) ? p : null;
}

function getDesktopCSS() {
  // Extra CSS for desktop-specific adjustments
  const titleBarCSS = IS_MAC ? `
    /* macOS: traffic lights spacing */
    #topbar { padding-left: 80px; -webkit-app-region: drag; }
    #topbar button, #topbar select, #topbar input { -webkit-app-region: no-drag; }
    #sidebar-header { -webkit-app-region: drag; padding-top: 16px; }
  ` : `
    /* Windows/Linux: custom title bar area */
    #desktop-titlebar { -webkit-app-region: drag; }
    #desktop-titlebar button { -webkit-app-region: no-drag; }
  `;

  return `
    ${titleBarCSS}
    /* Desktop: hide PWA / mobile-only elements */
    .pwa-only { display: none !important; }
    /* Smooth resize */
    body { transition: none; }
  `;
}

// ===== App Lifecycle =====
app.whenReady().then(() => {
  setupAPIProxy();
  createWindow();
  createMenu();
  createTray();
  setupIPC();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow?.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (!IS_MAC) app.quit();
});

app.on('before-quit', () => {
  app.isQuitting = true;
});
