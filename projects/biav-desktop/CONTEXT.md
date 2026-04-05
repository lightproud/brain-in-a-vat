# BIAV Desktop — 银芯系统桌面版

> 最后更新：2026-04-05 by Code-site

## 概述

缸中之脑银芯系统桌面版，基于 Electron 封装 Web 版。
零代码复制：构建脚本自动从 Web 版 (`../biav/index.html`) 生成桌面版 HTML。

## 架构

```
biav-desktop/
  main.js          — Electron 主进程（窗口管理、API 代理、系统托盘、菜单）
  preload.js       — 安全 IPC 桥接（contextBridge 暴露 biavDesktop API）
  desktop-init.js  — 渲染进程桌面适配层（标题栏、快捷键、文件保存、主题同步）
  build.js         — 构建脚本（Web HTML → Desktop HTML，自动注入适配）
  renderer/        — [生成] 构建产物目录（.gitignore 排除）
  assets/          — 应用图标（icon.png / icon.ico / icon.icns）
  package.json     — Electron + electron-builder 配置
```

## Web → Desktop 适配策略

构建脚本 (`build.js`) 对 Web 版 HTML 执行以下自动修改：

1. **移除 Service Worker** — 桌面版不需要 PWA 离线缓存
2. **移除 PWA 元标签** — manifest、apple-mobile-web-app 等
3. **移除 `anthropic-dangerous-direct-browser-access`** — 通过 Electron 主进程 API 代理解决 CORS
4. **注入自定义标题栏** — Windows/Linux 无边框窗口的最小化/最大化/关闭按钮
5. **注入桌面 CSS** — 拖拽区域、macOS 红绿灯间距、滚动条优化
6. **注入 `desktop-init.js`** — 连接 IPC 桥接到 Web 应用现有功能

## 主进程能力

- **API 代理**：webRequest 拦截 Anthropic API 请求，处理 CORS 头
- **窗口状态持久化**：记忆窗口位置和大小
- **原生菜单**：完整中文菜单栏（文件/编辑/视图/窗口/帮助）
- **系统托盘**：最小化到托盘，右键菜单快捷操作
- **全局快捷键**：Ctrl+N 新对话、Ctrl+K 搜索、Ctrl+, 设置等
- **原生文件对话框**：保存生成的文件到本地（替代浏览器下载）
- **系统主题同步**：跟随 OS 明暗模式自动切换

## 开发

```bash
cd projects/biav-desktop
npm install
node build.js          # 生成 renderer/index.html
npm start              # 启动 Electron
npm run dev            # 开发模式（含 DevTools）
```

## 打包

```bash
npm run build          # 构建当前平台安装包
npm run build:win      # Windows (NSIS + Portable)
npm run build:mac      # macOS (DMG)
npm run build:linux    # Linux (AppImage + DEB)
```

## 技术栈

- Electron 33+
- electron-builder（打包）
- electron-store（可选，持久化配置）
- 渲染层复用 Web 版全部功能（179KB 单文件 HTML）
