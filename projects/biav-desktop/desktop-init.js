// ===== Desktop Bridge (injected into renderer) =====
// Connects Electron IPC to the web app's existing functionality
(function initDesktop() {
  if (typeof window.biavDesktop === 'undefined') return; // Not in Electron

  const D = window.biavDesktop;

  // Mark platform on body for CSS targeting
  document.body.classList.add('is-desktop', 'platform-' + D.platform);

  // ===== Window Controls (Windows/Linux custom title bar) =====
  const tbMin = document.getElementById('tb-minimize');
  const tbMax = document.getElementById('tb-maximize');
  const tbClose = document.getElementById('tb-close');

  if (tbMin) tbMin.addEventListener('click', () => D.windowMinimize());
  if (tbMax) tbMax.addEventListener('click', () => D.windowMaximize());
  if (tbClose) tbClose.addEventListener('click', () => D.windowClose());

  // Update maximize button icon on state change
  if (D.onWindowMaximized) {
    D.onWindowMaximized((isMax) => {
      if (!tbMax) return;
      tbMax.innerHTML = isMax
        ? '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1"><rect x="0.5" y="2.5" width="7" height="7"/><polyline points="2.5,2.5 2.5,0.5 9.5,0.5 9.5,7.5 7.5,7.5"/></svg>'
        : '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1"><rect x="0.5" y="0.5" width="9" height="9"/></svg>';
      tbMax.title = isMax ? '还原' : '最大化';
    });
  }

  // ===== Keyboard Shortcuts from Menu =====
  if (D.onShortcut) {
    D.onShortcut((action) => {
      switch (action) {
        case 'new-chat':
          document.getElementById('new-chat-btn')?.click();
          break;
        case 'search': {
          const searchInput = document.getElementById('conv-search');
          if (searchInput) {
            // Ensure sidebar is visible and chat panel is active
            const sidebar = document.getElementById('sidebar');
            if (sidebar?.classList.contains('hidden')) {
              document.getElementById('toggle-sidebar')?.click();
            }
            const chatTab = document.querySelector('.sb-tab[data-panel="chat"]');
            if (chatTab && !chatTab.classList.contains('active')) chatTab.click();
            searchInput.focus();
          }
          break;
        }
        case 'settings':
          document.getElementById('settings-btn')?.click();
          break;
        case 'toggle-sidebar':
          document.getElementById('toggle-sidebar')?.click();
          break;
        case 'toggle-theme':
          document.getElementById('theme-btn')?.click();
          break;
        case 'export':
          document.getElementById('export-btn')?.click();
          break;
      }
    });
  }

  // ===== Enhanced File Save (native dialog) =====
  // Override the web's downloadFile to use native save dialog for generated files
  const origDownloadFile = window.downloadFile;
  window.downloadFile = async function(fileId) {
    const f = window._fileRegistry?.[fileId];
    if (!f || !D.saveFile) {
      // Fallback to web behavior
      if (origDownloadFile) origDownloadFile(fileId);
      return;
    }
    try {
      const arrayBuf = await f.blob.arrayBuffer();
      const result = await D.saveFile(
        Array.from(new Uint8Array(arrayBuf)),
        f.filename,
        getFilters(f.filename)
      );
      if (result) {
        console.log('File saved to:', result);
      }
    } catch (e) {
      // Fallback to web download
      if (origDownloadFile) origDownloadFile(fileId);
    }
  };

  function getFilters(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const map = {
      pdf: [{ name: 'PDF 文件', extensions: ['pdf'] }],
      doc: [{ name: 'Word 文件', extensions: ['doc'] }],
      docx: [{ name: 'Word 文件', extensions: ['docx'] }],
      xlsx: [{ name: 'Excel 文件', extensions: ['xlsx'] }],
      pptx: [{ name: 'PowerPoint 文件', extensions: ['pptx'] }],
      png: [{ name: 'PNG 图片', extensions: ['png'] }],
      svg: [{ name: 'SVG 图片', extensions: ['svg'] }],
      mid: [{ name: 'MIDI 文件', extensions: ['mid'] }],
      html: [{ name: 'HTML 文件', extensions: ['html'] }],
    };
    return map[ext] || [{ name: '所有文件', extensions: ['*'] }];
  }

  // ===== System Theme Sync =====
  if (D.onSystemThemeChanged) {
    D.onSystemThemeChanged((theme) => {
      // Only auto-switch if user hasn't manually set a preference
      const userPref = localStorage.getItem('biav-theme');
      if (!userPref || userPref === 'system') {
        document.documentElement.classList.toggle('light', theme === 'light');
      }
    });
  }

  // ===== Update Version Display =====
  D.getAppInfo?.().then((info) => {
    document.querySelectorAll('.ver,[id="sidebar-footer"]').forEach(el => {
      el.textContent = 'v' + info.version + ' Desktop';
    });
  });

  // ===== Double-click title bar to maximize (Windows/Linux) =====
  const titlebar = document.getElementById('desktop-titlebar');
  if (titlebar) {
    titlebar.addEventListener('dblclick', (e) => {
      if (e.target === titlebar || e.target.closest('[style*="flex:1"]')) {
        D.windowMaximize();
      }
    });
  }

  console.log('🖥️ BIAV Desktop initialized');
})();
