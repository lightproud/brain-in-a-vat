#!/usr/bin/env node
/**
 * Build script: generates desktop renderer HTML from the web version.
 *
 * Usage:
 *   node build.js          — sync web HTML → renderer/index.html
 *   node build.js --watch  — watch for changes
 */

const fs = require('fs');
const path = require('path');

const WEB_HTML = path.join(__dirname, '..', 'biav', 'index.html');
const OUT_DIR = path.join(__dirname, 'renderer');
const OUT_HTML = path.join(OUT_DIR, 'index.html');
const DESKTOP_INIT = path.join(__dirname, 'desktop-init.js');

function build() {
  if (!fs.existsSync(WEB_HTML)) {
    console.error('❌ Web version not found:', WEB_HTML);
    process.exit(1);
  }

  fs.mkdirSync(OUT_DIR, { recursive: true });

  let html = fs.readFileSync(WEB_HTML, 'utf8');

  // 1. Remove Service Worker registration block
  html = html.replace(
    /\/\/ Register Service Worker.*?(?=\n<\/script>)/s,
    '// Service Worker disabled in desktop mode'
  );

  // 2. Remove PWA manifest link
  html = html.replace(/<link rel="manifest"[^>]*>\n?/, '');

  // 3. Remove mobile-web-app meta tags (keep viewport for layout)
  html = html.replace(/<meta name="apple-mobile-web-app-capable"[^>]*>\n?/g, '');
  html = html.replace(/<meta name="apple-mobile-web-app-status-bar-style"[^>]*>\n?/g, '');
  html = html.replace(/<meta name="apple-mobile-web-app-title"[^>]*>\n?/g, '');
  html = html.replace(/<meta name="mobile-web-app-capable"[^>]*>\n?/g, '');

  // 4. Remove 'anthropic-dangerous-direct-browser-access' header from fetch calls
  html = html.replace(
    /['"]anthropic-dangerous-direct-browser-access['"]:\s*['"]true['"],?\n?\s*/g,
    ''
  );

  // 5. Inject desktop title bar for Windows/Linux BEFORE <div id="app">
  const titleBar = `
<!-- Desktop Title Bar (Windows/Linux) -->
<div id="desktop-titlebar" style="display:none;height:32px;background:var(--bg);border-bottom:1px solid var(--border);align-items:center;padding:0 8px;-webkit-app-region:drag;flex-shrink:0;position:relative;z-index:999">
  <div style="display:flex;align-items:center;gap:8px;-webkit-app-region:no-drag">
    <span style="font-size:12px;color:var(--gold);font-weight:700;font-family:'Noto Serif SC',serif;letter-spacing:1px;margin-left:8px">缸中之脑</span>
  </div>
  <div style="flex:1"></div>
  <div id="titlebar-controls" style="display:flex;-webkit-app-region:no-drag">
    <button class="tb-btn" id="tb-minimize" title="最小化" style="width:46px;height:32px;border:none;background:none;color:var(--text-dim);cursor:pointer;display:flex;align-items:center;justify-content:center">
      <svg width="10" height="1" viewBox="0 0 10 1"><rect width="10" height="1" fill="currentColor"/></svg>
    </button>
    <button class="tb-btn" id="tb-maximize" title="最大化" style="width:46px;height:32px;border:none;background:none;color:var(--text-dim);cursor:pointer;display:flex;align-items:center;justify-content:center">
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1"><rect x="0.5" y="0.5" width="9" height="9"/></svg>
    </button>
    <button class="tb-btn tb-close" id="tb-close" title="关闭" style="width:46px;height:32px;border:none;background:none;color:var(--text-dim);cursor:pointer;display:flex;align-items:center;justify-content:center">
      <svg width="10" height="10" viewBox="0 0 10 10" stroke="currentColor" stroke-width="1.2"><line x1="0" y1="0" x2="10" y2="10"/><line x1="10" y1="0" x2="0" y2="10"/></svg>
    </button>
  </div>
</div>
`;
  html = html.replace('<div id="app">', titleBar + '\n<div id="app">');

  // 6. Inject desktop CSS before </style>
  const desktopCSS = `
/* ===== Desktop Adaptations ===== */
#desktop-titlebar .tb-btn:hover { background: var(--bg-hover); color: var(--text); }
#desktop-titlebar .tb-close:hover { background: #c42b1c !important; color: #fff !important; }
body.platform-darwin #desktop-titlebar { display: none !important; }
body.platform-win32 #desktop-titlebar,
body.platform-linux #desktop-titlebar { display: flex !important; }
/* macOS: drag area on topbar */
body.platform-darwin #topbar { -webkit-app-region: drag; padding-left: 80px; }
body.platform-darwin #topbar button,
body.platform-darwin #topbar select,
body.platform-darwin #topbar input,
body.platform-darwin #topbar .topbar-btn,
body.platform-darwin #model-select-wrap,
body.platform-darwin #prompt-wrap,
body.platform-darwin #style-wrap { -webkit-app-region: no-drag; }
body.platform-darwin #sidebar-header { padding-top: 38px; }
/* Desktop: no safe area padding */
body.is-desktop #input-area { padding-bottom: 12px; }
body.is-desktop #topbar { padding-top: 12px; }
/* Desktop: smoother scrollbar */
body.is-desktop ::-webkit-scrollbar { width: 8px; }
body.is-desktop ::-webkit-scrollbar-thumb { border-radius: 4px; }
`;
  html = html.replace('</style>', desktopCSS + '\n</style>');

  // 7. Inject desktop initialization script before </script>
  let desktopJS = '';
  if (fs.existsSync(DESKTOP_INIT)) {
    desktopJS = fs.readFileSync(DESKTOP_INIT, 'utf8');
  }
  html = html.replace(
    '</script>\n</body>',
    '\n' + desktopJS + '\n</script>\n</body>'
  );

  // 8. Update title
  html = html.replace(
    '<title>缸中之脑 / Brain in a Vat</title>',
    '<title>缸中之脑 — 银芯系统桌面版</title>'
  );

  fs.writeFileSync(OUT_HTML, html, 'utf8');
  console.log(`✅ Desktop HTML generated: ${OUT_HTML} (${(Buffer.byteLength(html) / 1024).toFixed(1)} KB)`);
}

// Run
build();

if (process.argv.includes('--watch')) {
  console.log('👀 Watching for changes...');
  fs.watchFile(WEB_HTML, { interval: 1000 }, () => {
    console.log('🔄 Web version changed, rebuilding...');
    build();
  });
  if (fs.existsSync(DESKTOP_INIT)) {
    fs.watchFile(DESKTOP_INIT, { interval: 1000 }, () => {
      console.log('🔄 Desktop init changed, rebuilding...');
      build();
    });
  }
}
