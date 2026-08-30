// ============================================================
// SMART SALES ANALYTICS - THEME MANAGER
// Handles theme selection, persistence, and application
// ============================================================

class ThemeManager {
  constructor() {
    this.STORAGE_KEY = 'smartsales_theme';
    this.LAYOUT_STORAGE_KEY = 'smartsales_layout';
    this.FONT_SIZE_STORAGE_KEY = 'smartsales_font_size';
    this.NOTIFICATIONS_STORAGE_KEY = 'smartsales_notifications';
    this.SIDEBAR_STORAGE_KEY = 'smartsales_sidebar_collapsed';

    this.themes = ['light', 'black', 'grey', 'white', 'bw'];
    this.layouts = ['comfortable', 'compact'];
    this.fontSizes = ['small', 'medium', 'large'];

    this.init();
  }

  init() {
    // Apply saved theme on page load
    const savedTheme = this.getTheme();
    this.applyTheme(savedTheme);

    // Apply saved layout
    const savedLayout = this.getLayout();
    this.applyLayout(savedLayout);

    // Apply saved font size
    const savedFontSize = this.getFontSize();
    this.applyFontSize(savedFontSize);

    // Apply saved sidebar state
    const sidebarCollapsed = this.isSidebarCollapsed();
    if (sidebarCollapsed) {
      this.toggleSidebar();
    }

    // Apply saved notifications setting
    const notificationsEnabled = this.areNotificationsEnabled();
    this.setNotifications(notificationsEnabled);
  }

  // ============================================================
  // THEME METHODS
  // ============================================================

  getTheme() {
    return localStorage.getItem(this.STORAGE_KEY) || 'light';
  }

  setTheme(theme) {
    if (!this.themes.includes(theme)) {
      console.warn(`Invalid theme: ${theme}`);
      return false;
    }
    localStorage.setItem(this.STORAGE_KEY, theme);
    this.applyTheme(theme);
    this.updateThemeUI(theme);
    return true;
  }

  applyTheme(theme) {
    // Remove all theme classes
    this.themes.forEach(t => {
      if (t !== 'light') {
        document.documentElement.classList.remove(`theme-${t}`);
      }
    });

    // Apply selected theme class (default light theme has no class)
    if (theme !== 'light') {
      document.documentElement.classList.add(`theme-${theme}`);
    }

    // Update chart images if they exist (charts may need regeneration for some themes)
    // This could trigger a regenerate-charts endpoint if needed
  }

  updateThemeUI(theme) {
    // Update all theme preview cards to show which is active
    document.querySelectorAll('.theme-preview').forEach(preview => {
      const previewTheme = preview.dataset.theme;
      if (previewTheme === theme) {
        preview.classList.add('active');
        const checkmark = preview.querySelector('.theme-preview-check');
        if (checkmark) {
          checkmark.innerHTML = '✓';
        }
      } else {
        preview.classList.remove('active');
        const checkmark = preview.querySelector('.theme-preview-check');
        if (checkmark) {
          checkmark.innerHTML = '';
        }
      }
    });
  }

  // ============================================================
  // LAYOUT METHODS
  // ============================================================

  getLayout() {
    return localStorage.getItem(this.LAYOUT_STORAGE_KEY) || 'comfortable';
  }

  setLayout(layout) {
    if (!this.layouts.includes(layout)) {
      console.warn(`Invalid layout: ${layout}`);
      return false;
    }
    localStorage.setItem(this.LAYOUT_STORAGE_KEY, layout);
    this.applyLayout(layout);
    this.updateLayoutUI(layout);
    return true;
  }

  applyLayout(layout) {
    const root = document.documentElement;
    if (layout === 'compact') {
      root.style.setProperty('--spacing-multiplier', '0.75');
    } else {
      root.style.setProperty('--spacing-multiplier', '1');
    }
    document.body.dataset.layout = layout;
  }

  updateLayoutUI(layout) {
    document.querySelectorAll('[data-layout-option]').forEach(radio => {
      const isSelected = radio.value === layout;
      radio.checked = isSelected;
      const label = radio.closest('label');
      if (label) {
        if (isSelected) {
          label.style.borderColor = 'var(--brand)';
          label.style.backgroundColor = 'var(--brand-soft)';
        } else {
          label.style.borderColor = 'var(--border)';
          label.style.backgroundColor = 'transparent';
        }
      }
    });
  }

  // ============================================================
  // FONT SIZE METHODS
  // ============================================================

  getFontSize() {
    return localStorage.getItem(this.FONT_SIZE_STORAGE_KEY) || 'medium';
  }

  setFontSize(size) {
    if (!this.fontSizes.includes(size)) {
      console.warn(`Invalid font size: ${size}`);
      return false;
    }
    localStorage.setItem(this.FONT_SIZE_STORAGE_KEY, size);
    this.applyFontSize(size);
    this.updateFontSizeUI(size);
    return true;
  }

  applyFontSize(size) {
    const root = document.documentElement;
    const sizeMap = {
      'small': '14px',
      'medium': '16px',
      'large': '18px'
    };
    root.style.setProperty('--font-size-base', sizeMap[size] || '16px');
  }

  updateFontSizeUI(size) {
    document.querySelectorAll('[data-font-size-option]').forEach(radio => {
      const isSelected = radio.value === size;
      radio.checked = isSelected;
    });
  }

  // ============================================================
  // NOTIFICATIONS METHODS
  // ============================================================

  areNotificationsEnabled() {
    const value = localStorage.getItem(this.NOTIFICATIONS_STORAGE_KEY);
    return value === null ? true : value === 'true';
  }

  setNotifications(enabled) {
    localStorage.setItem(this.NOTIFICATIONS_STORAGE_KEY, enabled);
    this.updateNotificationsUI(enabled);
  }

  updateNotificationsUI(enabled) {
    const toggle = document.querySelector('[data-notifications-toggle]');
    if (toggle) {
      toggle.checked = enabled;
    }
  }

  // ============================================================
  // SIDEBAR METHODS
  // ============================================================

  isSidebarCollapsed() {
    return localStorage.getItem(this.SIDEBAR_STORAGE_KEY) === 'true';
  }

  toggleSidebar() {
    const isCollapsed = this.isSidebarCollapsed();
    localStorage.setItem(this.SIDEBAR_STORAGE_KEY, !isCollapsed);
    this.applySidebarState(!isCollapsed);
  }

  applySidebarState(isCollapsed) {
    const sidebar = document.querySelector('.sidebar');
    const contentArea = document.querySelector('.content-area');
    
    if (isCollapsed) {
      sidebar?.classList.add('collapsed');
      contentArea?.classList.add('sidebar-collapsed');
    } else {
      sidebar?.classList.remove('collapsed');
      contentArea?.classList.remove('sidebar-collapsed');
    }

    const toggle = document.querySelector('[data-sidebar-toggle]');
    if (toggle) {
      toggle.checked = isCollapsed;
    }
  }

  // ============================================================
  // RESET METHODS
  // ============================================================

  resetToDefaults() {
    localStorage.removeItem(this.STORAGE_KEY);
    localStorage.removeItem(this.LAYOUT_STORAGE_KEY);
    localStorage.removeItem(this.FONT_SIZE_STORAGE_KEY);
    localStorage.removeItem(this.NOTIFICATIONS_STORAGE_KEY);
    localStorage.removeItem(this.SIDEBAR_STORAGE_KEY);

    this.applyTheme('light');
    this.applyLayout('comfortable');
    this.applyFontSize('medium');
    this.setNotifications(true);
    this.applySidebarState(false);

    this.updateThemeUI('light');
    this.updateLayoutUI('comfortable');
    this.updateFontSizeUI('medium');
    this.updateNotificationsUI(true);
  }

  // ============================================================
  // SAVE SETTINGS
  // ============================================================

  saveSettings() {
    // All individual settings are saved as they're changed
    // This method can be used to sync settings to server if needed
    return {
      theme: this.getTheme(),
      layout: this.getLayout(),
      fontSize: this.getFontSize(),
      notifications: this.areNotificationsEnabled(),
      sidebarCollapsed: this.isSidebarCollapsed()
    };
  }
}

// Initialize theme manager when DOM is ready
let themeManager;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    themeManager = new ThemeManager();
  });
} else {
  themeManager = new ThemeManager();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
}
