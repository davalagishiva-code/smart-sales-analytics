document.addEventListener('DOMContentLoaded', () => {
  const navButtons = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.page-section');
  const sidebar = document.getElementById('sidebar');
  const sidebarClose = document.getElementById('sidebarClose');
  const menuToggle = document.getElementById('menuToggle');
  const profileToggle = document.getElementById('profileToggle');
  const profilePanel = document.getElementById('profilePanel');
  const globalSearch = document.getElementById('globalSearch');
  const refreshDashboardBtn = document.getElementById('refreshDashboardBtn');
  const lastUpdatedText = document.getElementById('lastUpdatedText');
  const rangeButtons = document.querySelectorAll('.range-btn');

  function closeSidebar() {
    if (sidebar) {
      sidebar.classList.remove('open');
    }
  }

  function openSidebar() {
    if (sidebar) {
      sidebar.classList.add('open');
    }
  }

  function showSection(sectionId) {
    navButtons.forEach((button) => {
      button.classList.toggle('active', button.dataset.section === sectionId);
    });

    sections.forEach((section) => {
      section.classList.toggle('active', section.id === sectionId);
    });

    closeSidebar();
  }

  navButtons.forEach((button) => {
    button.addEventListener('click', () => showSection(button.dataset.section));
  });

  document.querySelectorAll('.dashboard-action-btn').forEach((button) => {
    button.addEventListener('click', () => showSection(button.dataset.target));
  });

  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      if (sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (sidebarClose) {
    sidebarClose.addEventListener('click', closeSidebar);
  }

  if (window.innerWidth <= 900) {
    document.addEventListener('click', (event) => {
      const clickedInsideSidebar = sidebar && sidebar.contains(event.target);
      const clickedToggle = menuToggle && menuToggle.contains(event.target);
      if (!clickedInsideSidebar && !clickedToggle && sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
      }
    });
  }

  if (profileToggle && profilePanel) {
    profileToggle.addEventListener('click', () => {
      const isHidden = profilePanel.hasAttribute('hidden');
      profilePanel.toggleAttribute('hidden', !isHidden);
      profileToggle.setAttribute('aria-expanded', String(isHidden));
    });
    document.addEventListener('click', (event) => {
      if (!profilePanel.contains(event.target) && !profileToggle.contains(event.target)) {
        profilePanel.setAttribute('hidden', 'hidden');
        profileToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  if (globalSearch) {
    globalSearch.addEventListener('input', () => {
      const term = globalSearch.value.trim();
      const historySearch = document.getElementById('historySearch');
      if (historySearch) {
        historySearch.value = term;
      }
      if (term) {
        showSection('sales-history');
      }
      if (typeof loadSalesHistory === 'function') {
        loadSalesHistory();
      }
    });
  }

  const dashboardStatus = document.getElementById('dashboardStatus');
  const dashboardKpis = document.getElementById('dashboardKpis');
  const recentSalesTableBody = document.getElementById('recentSalesTableBody');
  const topPerformersGrid = document.getElementById('topPerformersGrid');
  const productsTableBody = document.getElementById('productsTableBody');
  const customersTableBody = document.getElementById('customersTableBody');
  const customersSummaryGrid = document.getElementById('customersSummaryGrid');
  const customersPagination = document.getElementById('customersPagination');
  const customersSearch = document.getElementById('customersSearch');
  const customersTypeFilter = document.getElementById('customersTypeFilter');
  const customersStatusFilter = document.getElementById('customersStatusFilter');
  const customersSortBy = document.getElementById('customersSortBy');
  const customerModal = document.getElementById('customerModal');
  const customerForm = document.getElementById('customerForm');
  const customerFormTitle = document.getElementById('customerFormTitle');
  const customerFormMessage = document.getElementById('customerFormMessage');
  const reportsTableBody = document.getElementById('reportsTableBody');
  const historyTableBody = document.getElementById('historyTableBody');
  const productForm = document.getElementById('productForm');
  const productModal = document.getElementById('productModal');
  const productFormTitle = document.getElementById('productFormTitle');
  const productsSearch = document.getElementById('productsSearch');
  const productsCategoryFilter = document.getElementById('productsCategoryFilter');
  const productsStatusFilter = document.getElementById('productsStatusFilter');
  const productsSortBy = document.getElementById('productsSortBy');
  const productsSummary = document.getElementById('productsSummary');
  const dbStatus = document.getElementById('dbStatus');
  const saleForm = document.getElementById('saleForm');
  const saleSuccessMessage = document.getElementById('saleSuccessMessage');
  const predictionForm = document.getElementById('predictionForm');
  const predictionResult = document.getElementById('predictionResult');
  const analysisFilterForm = document.getElementById('analysisFilterForm');
  const analysisStatus = document.getElementById('analysisStatus');
  const analysisResetBtn = document.getElementById('analysisResetBtn');
  const analysisStartDate = document.getElementById('analysisStartDate');
  const analysisEndDate = document.getElementById('analysisEndDate');
  const historyCategoryFilter = document.getElementById('historyCategoryFilter');
  const analysisCategory = document.getElementById('analysisCategory');
  const analysisRegion = document.getElementById('analysisRegion');
  const analysisPaymentMethod = document.getElementById('analysisPaymentMethod');
  const backendUrlDisplay = document.getElementById('backendUrlDisplay');
  if (backendUrlDisplay) {
    backendUrlDisplay.textContent = window.API_CONFIG.baseUrl;
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(Number(value || 0));
  }

  function formatCompact(value) {
    return new Intl.NumberFormat('en-IN', {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(Number(value || 0));
  }

  function setError(element, message) {
    if (!element) return;
    element.textContent = message;
    element.classList.add('error');
  }

  function clearError(element) {
    if (!element) return;
    element.textContent = '';
    element.classList.remove('error');
  }

  function renderKpiCard(title, value, meta, icon) {
    return `
      <div class="kpi-card">
        <div class="kpi-head">
          <div>
            <div class="kpi-label">${title}</div>
          </div>
          <div class="kpi-icon">${icon}</div>
        </div>
        <div class="kpi-value">${value}</div>
        <div class="kpi-meta">${meta}</div>
      </div>
    `;
  }

  function renderMetricCard(label, value) {
    return `
      <div class="summary-card">
        <div class="label">${label}</div>
        <div class="value">${value}</div>
      </div>
    `;
  }

  function formatCompactCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(Number(value || 0));
  }

  function renderChart(containerId, items, labelKey, valueKey, formatter = (value) => value) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!items || !items.length) {
      container.innerHTML = '<div class="chart-placeholder">No data available</div>';
      return;
    }

    const maxValue = Math.max(...items.map((item) => Number(item[valueKey] || 0)), 1);
    const html = items.map((item) => {
      const label = item[labelKey] || 'N/A';
      const numericValue = Number(item[valueKey] || 0);
      const width = ((numericValue / maxValue) * 100).toFixed(2);

      return `
        <div class="chart-bar-row" style="margin-bottom: 12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:6px;font-size:0.82rem;">
            <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:60%;">${label}</span>
            <strong>${formatter(numericValue)}</strong>
          </div>
          <div style="background:#e2e8f0;border-radius:999px;overflow:hidden;height:10px;width:100%;">
            <div style="width:${width}%;background:linear-gradient(90deg,#60a5fa,#2563eb);height:100%;border-radius:999px;"></div>
          </div>
        </div>
      `;
    }).join('');

    container.innerHTML = html;
  }

  function renderDashboardKpis(data) {
    if (!dashboardKpis) return;

    const cards = [
      renderKpiCard('Total Revenue', formatCurrency(data.total_revenue || 0), `${formatCompact(data.total_orders || 0)} orders`, '₹'),
      renderKpiCard('Total Orders', `${data.total_orders || 0}`, `${formatCompact(data.units_sold || 0)} units sold`, '🧾'),
      renderKpiCard('Units Sold', `${data.units_sold || 0}`, `${formatCompact(data.total_customers || 0)} customers`, '📦'),
      renderKpiCard('Average Order Value', formatCurrency(data.average_order_value || 0), `${formatCompact(data.total_products || 0)} products`, '📈'),
      renderKpiCard('Total Customers', `${data.total_customers || 0}`, 'active buyers', '👥'),
      renderKpiCard('Total Products', `${data.total_products || 0}`, 'catalog items', '🛍️'),
    ];

    dashboardKpis.innerHTML = cards.join('');
  }

  function renderRecentSales(sales) {
    if (!recentSalesTableBody) return;
    if (!sales || !sales.length) {
      recentSalesTableBody.innerHTML = '<tr><td colspan="6">No recent sales available.</td></tr>';
      return;
    }

    recentSalesTableBody.innerHTML = sales.slice(0, 8).map((sale) => `
      <tr>
        <td>${sale.date || 'N/A'}</td>
        <td>${sale.customer || 'N/A'}</td>
        <td>${sale.product || 'N/A'}</td>
        <td>${sale.category || 'N/A'}</td>
        <td>${formatCurrency(sale.total_amount || 0)}</td>
        <td>${sale.payment_method || 'N/A'}</td>
      </tr>
    `).join('');
  }

  function renderTopPerformers(data) {
    if (!topPerformersGrid) return;
    const performers = [
      { label: 'Top Product', value: data?.product?.name || 'N/A', meta: formatCurrency(data?.product?.value || 0) },
      { label: 'Top Category', value: data?.category?.name || 'N/A', meta: formatCurrency(data?.category?.value || 0) },
      { label: 'Top Region', value: data?.region?.name || 'N/A', meta: formatCurrency(data?.region?.value || 0) },
      { label: 'Top Customer', value: data?.customer?.name || 'N/A', meta: formatCurrency(data?.customer?.value || 0) },
    ];

    topPerformersGrid.innerHTML = performers.map((item) => `
      <div class="performer-card">
        <div class="label">${item.label}</div>
        <div class="value">${item.value}</div>
        <small>${item.meta}</small>
      </div>
    `).join('');
  }

  function renderVerticalBarChart(containerId, items, labelKey, valueKey, formatter = (value) => value, valueLabel = 'value', accentColor = '#2563eb') {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<div class="chart-placeholder">No data available</div>';
      return;
    }

    const width = 540;
    const height = 260;
    const margin = { top: 18, right: 18, bottom: 42, left: 34 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const maxValue = Math.max(...items.map((item) => Number(item[valueKey] || 0)), 1);
    const barWidth = Math.max(chartWidth / items.length * 0.62, 22);
    const gap = chartWidth / items.length;
    const gradientId = `barGradient-${containerId}`;

    container.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${containerId} chart">
        <defs>
          <linearGradient id="${gradientId}" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stop-color="${accentColor}" />
            <stop offset="100%" stop-color="${accentColor}" />
          </linearGradient>
        </defs>
        ${Array.from({ length: 5 }).map((_, index) => {
          const y = margin.top + (chartHeight / 4) * index;
          const tickValue = maxValue * (1 - index / 4);
          return `
            <g>
              <line x1="${margin.left}" x2="${width - margin.right}" y1="${y}" y2="${y}" stroke="#e2e8f0" stroke-width="1" />
              <text x="4" y="${y + 4}" font-size="10" fill="#64748b">${formatter(tickValue).replace(/\s+/g, '').slice(0, 8)}</text>
            </g>
          `;
        }).join('')}
        ${items.map((item, index) => {
          const value = Number(item[valueKey] || 0);
          const x = margin.left + index * gap + (gap - barWidth) / 2;
          const barHeight = (value / maxValue) * chartHeight;
          const y = margin.top + chartHeight - barHeight;
          const label = String(item[labelKey] || 'N/A');
          const shortLabel = label.length > 10 ? `${label.slice(0, 9)}…` : label;
          return `
            <g>
              <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" rx="8" fill="url(#${gradientId})">
                <title>${label}: ${formatter(value)}</title>
              </rect>
              <text x="${x + barWidth / 2}" y="${height - 10}" text-anchor="middle" font-size="10" fill="#64748b">${shortLabel}</text>
            </g>
          `;
        }).join('')}
      </svg>
    `;
    container.dataset.chartType = 'vertical-bar';
  }

  function renderHorizontalBarChart(containerId, items, labelKey, valueKey, formatter = (value) => value, accentColor = '#2563eb') {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<div class="chart-placeholder">No data available</div>';
      return;
    }

    const width = 540;
    const height = 260;
    const margin = { top: 16, right: 22, bottom: 16, left: 140 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const maxValue = Math.max(...items.map((item) => Number(item[valueKey] || 0)), 1);
    const rowHeight = Math.min(26, (chartHeight / items.length) * 0.8);

    container.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${containerId} chart">
        <defs>
          <linearGradient id="horizontalBarGradient-${containerId}" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stop-color="${accentColor}" />
            <stop offset="100%" stop-color="${accentColor}" />
          </linearGradient>
        </defs>
        ${items.map((item, index) => {
          const value = Number(item[valueKey] || 0);
          const label = String(item[labelKey] || 'N/A');
          const barWidth = (value / maxValue) * chartWidth;
          const y = margin.top + index * (chartHeight / items.length) + 10;
          const labelY = y + rowHeight / 2 + 4;
          const x = margin.left;
          return `
            <g>
              <text x="${margin.left - 8}" y="${labelY}" text-anchor="end" font-size="10" fill="#475569">${label.length > 16 ? `${label.slice(0, 15)}…` : label}</text>
              <rect x="${x}" y="${y}" width="${chartWidth}" height="${rowHeight}" rx="8" fill="#e2e8f0"></rect>
              <rect x="${x}" y="${y}" width="${barWidth}" height="${rowHeight}" rx="8" fill="url(#horizontalBarGradient-${containerId})">
                <title>${label}: ${formatter(value)}</title>
              </rect>
            </g>
          `;
        }).join('')}
      </svg>
    `;
    container.dataset.chartType = 'horizontal-bar';
  }

  function renderLineChart(containerId, items, labelKey, valueKey, formatter = (value) => value, accentColor = '#2563eb') {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<div class="chart-placeholder">No data available</div>';
      return;
    }

    const width = 560;
    const height = 260;
    const margin = { top: 18, right: 18, bottom: 30, left: 38 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const values = items.map((item) => Number(item[valueKey] || 0));
    const maxValue = Math.max(...values, 1);
    const minValue = 0;
    const stepX = items.length > 1 ? chartWidth / (items.length - 1) : chartWidth;

    const points = items.map((item, index) => {
      const x = margin.left + index * stepX;
      const ratio = (Number(item[valueKey] || 0) - minValue) / Math.max(maxValue - minValue, 1);
      const y = margin.top + chartHeight - ratio * chartHeight;
      return { ...item, x, y };
    });

    const path = points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');
    const area = `${path} L ${points[points.length - 1].x} ${margin.top + chartHeight} L ${points[0].x} ${margin.top + chartHeight} Z`;
    const labelStep = Math.max(1, Math.ceil(items.length / 6));

    container.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${containerId} chart">
        <defs>
          <linearGradient id="lineArea-${containerId}" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stop-color="${accentColor}33" />
            <stop offset="100%" stop-color="${accentColor}08" />
          </linearGradient>
        </defs>
        ${Array.from({ length: 5 }).map((_, index) => {
          const y = margin.top + (chartHeight / 4) * index;
          return `<line x1="${margin.left}" x2="${width - margin.right}" y1="${y}" y2="${y}" stroke="#e2e8f0" stroke-width="1" />`;
        }).join('')}
        <path d="${area}" fill="url(#lineArea-${containerId})"></path>
        <path d="${path}" fill="none" stroke="${accentColor}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
        ${points.map((point, index) => `
          <g>
            <circle cx="${point.x}" cy="${point.y}" r="4.5" fill="${accentColor}">
              <title>${point[labelKey]}: ${formatter(Number(point[valueKey] || 0))}</title>
            </circle>
            ${index % labelStep === 0 || index === points.length - 1 ? `<text x="${point.x}" y="${height - 8}" text-anchor="middle" font-size="10" fill="#64748b">${String(point[labelKey]).slice(0,3)}</text>` : ''}
          </g>
        `).join('')}
      </svg>
    `;
    container.dataset.chartType = 'line';
  }

  function renderDonutChart(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<div class="chart-placeholder">No data available</div>';
      return;
    }

    const total = items.reduce((sum, item) => sum + Number(item.total || 0), 0) || 1;
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    let cumulative = 0;
    const palette = ['#2563eb', '#60a5fa', '#a78bfa', '#34d399', '#fbbf24', '#f87171'];

    const segments = items.map((item, index) => {
      const value = Number(item.total || 0);
      const fraction = value / total;
      const dash = fraction * circumference;
      const offset = -cumulative;
      cumulative += dash;
      return { ...item, value, fraction, dash, offset, color: palette[index % palette.length] };
    });

    container.innerHTML = `
      <div class="donut-wrap">
        <svg viewBox="0 0 160 160" width="140" height="140" role="img" aria-label="Payment method chart">
          <circle cx="80" cy="80" r="54" fill="none" stroke="#e2e8f0" stroke-width="22"></circle>
          ${segments.map((segment) => `
            <circle
              cx="80"
              cy="80"
              r="54"
              fill="none"
              stroke="${segment.color}"
              stroke-width="22"
              stroke-linecap="round"
              stroke-dasharray="${segment.dash} ${circumference - segment.dash}"
              stroke-dashoffset="${segment.offset}"
              transform="rotate(-90 80 80)"
            >
              <title>${segment.method || 'N/A'}: ${((segment.fraction || 0) * 100).toFixed(1)}% (${formatCurrency(segment.value)})</title>
            </circle>
          `).join('')}
        </svg>
        <div class="chart-legend">
          ${segments.map((segment, index) => `
            <div class="legend-item">
              <span class="legend-dot" style="background:${segment.color};"></span>
              <span>${segment.method || 'N/A'}</span>
              <strong>${((segment.fraction || 0) * 100).toFixed(0)}%</strong>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    container.dataset.chartType = 'donut';
  }

  function renderDashboardCharts(metrics) {
    renderLineChart('revenueTrendChart', metrics.monthly_revenue || [], 'month', 'total', (value) => formatCurrency(value));
    renderLineChart('monthlyChart', (metrics.monthly_revenue || []).slice(-6), 'month', 'total', (value) => formatCurrency(value));
    renderVerticalBarChart('categoryChart', metrics.category_performance || [], 'category', 'total', (value) => formatCurrency(value));
    renderHorizontalBarChart('productsChart', (metrics.top_products || []).slice(0, 5), 'product', 'revenue', (value) => formatCurrency(value));
    renderVerticalBarChart('regionChart', metrics.regional_sales || [], 'region', 'total', (value) => formatCurrency(value));
    renderDonutChart('paymentChart', metrics.payment_methods || []);
  }

  function renderScatterChart(containerId, items, accentColor = '#2563eb') {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<div class="chart-placeholder">No sales data available</div>';
      return;
    }

    const width = 560;
    const height = 300;
    const margin = { top: 20, right: 20, bottom: 36, left: 48 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const salesValues = items.map((item) => Number(item.sales || 0));
    const profitValues = items.map((item) => Number(item.profit || 0));
    const maxSales = Math.max(...salesValues, 1);
    const maxProfit = Math.max(...profitValues, 1);
    const minProfit = Math.min(...profitValues, 0);

    const points = items.map((item) => {
      const x = margin.left + (Number(item.sales || 0) / maxSales) * chartWidth;
      const y = margin.top + chartHeight - ((Number(item.profit || 0) - minProfit) / Math.max(maxProfit - minProfit, 1)) * chartHeight;
      return { ...item, x, y };
    });

    container.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Sales vs profit scatter chart">
        ${Array.from({ length: 5 }).map((_, idx) => {
          const y = margin.top + (chartHeight / 4) * idx;
          return `<line x1="${margin.left}" x2="${width - margin.right}" y1="${y}" y2="${y}" stroke="#e2e8f0" stroke-width="1" />`;
        }).join('')}
        ${Array.from({ length: 5 }).map((_, idx) => {
          const x = margin.left + (chartWidth / 4) * idx;
          return `<line x1="${x}" x2="${x}" y1="${margin.top}" y2="${height - margin.bottom}" stroke="#e2e8f0" stroke-width="1" />`;
        }).join('')}
        <line x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}" stroke="#94a3b8" />
        <line x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}" stroke="#94a3b8" />
        ${points.map((point) => `
          <g>
            <circle cx="${point.x}" cy="${point.y}" r="6" fill="${accentColor}" opacity="0.85">
              <title>${point.label}: Sales ${formatCurrency(point.sales)} • Profit ${formatCurrency(point.profit)} • Margin ${Number(point.profit_margin || 0).toFixed(1)}%</title>
            </circle>
          </g>
        `).join('')}
        <text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="10" fill="#64748b">Sales Revenue</text>
        <text x="16" y="${height / 2}" transform="rotate(-90 16 ${height / 2})" text-anchor="middle" font-size="10" fill="#64748b">Profit</text>
      </svg>
    `;
  }

  function renderComparisonPanel(containerId, comparison) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const metrics = [
      { key: 'revenue', label: 'Revenue' },
      { key: 'orders', label: 'Orders' },
      { key: 'profit', label: 'Profit' },
      { key: 'units_sold', label: 'Units Sold' },
      { key: 'profit_margin', label: 'Profit Margin' },
    ];

    container.innerHTML = metrics.map((metric) => {
      const current = comparison?.current?.[metric.key] ?? 0;
      const previous = comparison?.previous?.[metric.key] ?? 0;
      const change = comparison?.change?.[metric.key] ?? 0;
      const icon = change > 0 ? '↑' : change < 0 ? '↓' : '→';
      const deltaClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
      const valueLabel = metric.key === 'revenue' || metric.key === 'profit' ? formatCurrency(current) : metric.key === 'profit_margin' ? `${Number(current).toFixed(1)}%` : current;
      const prevLabel = metric.key === 'revenue' || metric.key === 'profit' ? formatCurrency(previous) : metric.key === 'profit_margin' ? `${Number(previous).toFixed(1)}%` : previous;
      return `
        <div class="comparison-item">
          <div class="title">${metric.label}</div>
          <div class="values">
            <span class="current">${valueLabel}</span>
            <span class="delta ${deltaClass}">${icon} ${Math.abs(change).toFixed(1)}%</span>
          </div>
          <div class="values">
            <span>Prev</span>
            <strong>${prevLabel}</strong>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderInsightsPanel(containerId, insights) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!insights || !insights.length) {
      container.innerHTML = '<div class="insight-item"><span class="insight-badge">i</span><span>No insights available.</span></div>';
      return;
    }

    container.innerHTML = insights.map((insight, index) => `
      <div class="insight-item">
        <span class="insight-badge">${index + 1}</span>
        <span>${insight}</span>
      </div>
    `).join('');
  }

  function renderPerformerMatrix(containerId, performers) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const items = [
      { label: 'Top Revenue Category', value: performers?.top_revenue_category?.category || 'N/A', metric: performers?.top_revenue_category?.total ? formatCurrency(performers.top_revenue_category.total) : 'N/A' },
      { label: 'Top Profit Category', value: performers?.top_profit_category?.category || 'N/A', metric: performers?.top_profit_category?.profit ? formatCurrency(performers.top_profit_category.profit) : 'N/A' },
      { label: 'Top Revenue Product', value: performers?.top_revenue_product?.product || 'N/A', metric: performers?.top_revenue_product?.revenue ? formatCurrency(performers.top_revenue_product.revenue) : 'N/A' },
      { label: 'Top Profit Product', value: performers?.top_profit_product?.product || 'N/A', metric: performers?.top_profit_product?.profit ? formatCurrency(performers.top_profit_product.profit) : 'N/A' },
      { label: 'Highest Margin Category', value: performers?.highest_profit_margin_category?.category || 'N/A', metric: performers?.highest_profit_margin_category?.margin ? `${Number(performers.highest_profit_margin_category.margin).toFixed(1)}%` : 'N/A' },
      { label: 'Highest Sales Region', value: performers?.highest_sales_region?.region || 'N/A', metric: performers?.highest_sales_region?.total ? formatCurrency(performers.highest_sales_region.total) : 'N/A' },
    ];

    container.innerHTML = items.map((item) => `
      <div class="performer-item">
        <div class="tag">${item.label}</div>
        <div class="name">${item.value}</div>
        <div class="amount">${item.metric}</div>
      </div>
    `).join('');
  }

  async function loadDashboard() {
    const activeRange = document.querySelector('.range-btn.active')?.dataset.range || 'all';
    try {
      const response = await apiRequest(`${window.API_CONFIG.endpoints.dashboard}?range=${encodeURIComponent(activeRange)}`);
      const metrics = response.metrics || {};
      const message = response.message || 'No sales data available';
      dashboardStatus.textContent = message;
      if (!metrics || Object.keys(metrics).length === 0 || Number(metrics.total_orders || 0) === 0) {
        dashboardKpis.innerHTML = '<div class="kpi-card"><div class="kpi-label">No data</div><div class="kpi-value">No sales data</div><div class="kpi-meta">Add sales to populate the dashboard.</div></div>';
        renderRecentSales([]);
        renderTopPerformers({});
        renderDashboardCharts({});
        return;
      }

      renderDashboardKpis(metrics);
      renderRecentSales(metrics.recent_sales || []);
      renderTopPerformers(metrics.top_performers || {});
      renderDashboardCharts(metrics);

      if (lastUpdatedText) {
        const now = new Date();
        lastUpdatedText.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
    } catch (error) {
      dashboardStatus.textContent = 'Unable to load dashboard data.';
      dashboardStatus.classList.add('error');
      console.error(error);
    }
  }

  rangeButtons.forEach((button) => {
    button.addEventListener('click', () => {
      rangeButtons.forEach((range) => range.classList.toggle('active', range === button));
      loadDashboard();
    });
  });

  if (refreshDashboardBtn) {
    refreshDashboardBtn.addEventListener('click', () => {
      loadDashboard();
    });
  }


  function escapeHtml(value) {
    return String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function getProductStatusLabel(status) {
    return {
      active: 'Active',
      'low-stock': 'Low stock',
      'out-of-stock': 'Out of stock',
      archived: 'Archived',
    }[status] || 'Active';
  }

  function renderProductsSummary(rows) {
    if (!productsSummary) return;
    const totalInventoryValue = rows.reduce((sum, row) => sum + Number(row.price || 0) * Number(row.stock || 0), 0);
    const lowStockCount = rows.filter((row) => Number(row.stock || 0) <= Number(row.min_stock || 0) && Number(row.stock || 0) > 0).length;
    const outOfStockCount = rows.filter((row) => Number(row.stock || 0) === 0).length;
    const revenue = rows.reduce((sum, row) => sum + Number(row.revenue || 0), 0);
    productsSummary.innerHTML = `
      <div class="summary-card">
        <div class="label">Inventory value</div>
        <div class="value">${formatCurrency(totalInventoryValue)}</div>
      </div>
      <div class="summary-card">
        <div class="label">Products</div>
        <div class="value">${rows.length}</div>
      </div>
      <div class="summary-card">
        <div class="label">Low stock</div>
        <div class="value">${lowStockCount}</div>
      </div>
      <div class="summary-card">
        <div class="label">Out of stock</div>
        <div class="value">${outOfStockCount}</div>
      </div>
      <div class="summary-card">
        <div class="label">Revenue</div>
        <div class="value">${formatCurrency(revenue)}</div>
      </div>
    `;
  }

  function getFilteredProducts(rows) {
    const searchTerm = (productsSearch?.value || '').trim().toLowerCase();
    const categoryFilter = productsCategoryFilter?.value || '';
    const statusFilter = productsStatusFilter?.value || '';
    const sortBy = productsSortBy?.value || 'name';

    const filtered = rows.filter((row) => {
      const haystack = [row.name, row.sku, row.category].join(' ').toLowerCase();
      const matchesSearch = !searchTerm || haystack.includes(searchTerm);
      const matchesCategory = !categoryFilter || String(row.category || '').toLowerCase() === categoryFilter.toLowerCase();
      const matchesStatus = !statusFilter || String(row.status || 'active') === statusFilter;
      return matchesSearch && matchesCategory && matchesStatus;
    });

    filtered.sort((a, b) => {
      const direction = 1;
      switch (sortBy) {
        case 'category':
          return String(a.category || '').localeCompare(String(b.category || '')) * direction;
        case 'stock':
          return (Number(b.stock || 0) - Number(a.stock || 0)) * direction;
        case 'price':
          return (Number(b.price || 0) - Number(a.price || 0)) * direction;
        case 'revenue':
          return (Number(b.revenue || 0) - Number(a.revenue || 0)) * direction;
        default:
          return String(a.name || '').localeCompare(String(b.name || '')) * direction;
      }
    });

    return filtered;
  }

  function populateProductCategoryOptions(rows) {
    if (!productsCategoryFilter) return;
    const categories = [...new Set(rows.map((row) => row.category).filter(Boolean))].sort();
    const currentValue = productsCategoryFilter.value;
    productsCategoryFilter.innerHTML = '<option value="">All categories</option>' + categories.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`).join('');
    if (categories.includes(currentValue)) {
      productsCategoryFilter.value = currentValue;
    }
  }

  function openProductModal(product = null) {
    const modal = document.getElementById('productModal');
    if (!modal) return;
    const form = document.getElementById('productForm');
    if (!form) return;
    const title = document.getElementById('productFormTitle');
    if (title) {
      title.textContent = product ? 'Edit Product' : 'Add Product';
    }
    form.dataset.productId = product ? product.id : '';

    const entries = form.querySelectorAll('input, select, textarea');
    entries.forEach((field) => {
      const name = field.name;
      if (!name) return;
      const value = product ? (product[name] ?? '') : '';
      if (field.type === 'number' && value === null) {
        field.value = 0;
      } else {
        field.value = product ? value : field.defaultValue || '';
      }
    });

    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    setTimeout(() => {
      const firstField = form.querySelector('input[name="name"]');
      if (firstField) firstField.focus();
    }, 20);
  }

  function closeProductModal() {
    const modal = document.getElementById('productModal');
    if (!modal) return;
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    const form = document.getElementById('productForm');
    if (form) form.reset();
    form?.removeAttribute('data-product-id');
  }

  async function loadProducts() {
    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.products);
      const rows = response.data || [];
      populateProductCategoryOptions(rows);
      renderProductsSummary(rows);
      const visibleRows = getFilteredProducts(rows);
      if (!visibleRows.length) {
        productsTableBody.innerHTML = '<tr><td colspan="7">No products match your current filters.</td></tr>';
        return;
      }
      productsTableBody.innerHTML = visibleRows.map((row) => {
        const statusText = getProductStatusLabel(row.status || 'active');
        const stock = Number(row.stock || 0);
        const minStock = Number(row.min_stock || 0);
        const statusClass = stock === 0 ? 'status-out' : stock <= minStock ? 'status-low' : 'status-active';
        return `
          <tr>
            <td>
              <div class="product-name-cell">
                <div class="product-badge">${escapeHtml((row.name || 'Unnamed').slice(0, 1).toUpperCase())}</div>
                <div>
                  <div class="product-name">${escapeHtml(row.name || 'Unnamed product')}</div>
                  <small>${escapeHtml(row.sku || 'No SKU')}</small>
                </div>
              </div>
            </td>
            <td>${escapeHtml(row.category || 'Uncategorized')}</td>
            <td>${formatCurrency(row.price || 0)}</td>
            <td>
              <div class="stock-cell">
                <strong>${stock}</strong>
                <span>min ${minStock}</span>
              </div>
            </td>
            <td><span class="product-status ${statusClass}">${statusText}</span></td>
            <td>${formatCurrency(row.revenue || 0)}</td>
            <td>
              <div class="product-action-cell">
                <button class="table-action-btn edit-product" type="button" data-product-id="${row.id}">Edit</button>
                <button class="table-action-btn danger delete-product" type="button" data-product-id="${row.id}">Delete</button>
              </div>
            </td>
          </tr>
        `;
      }).join('');

      document.querySelectorAll('.edit-product').forEach((button) => {
        button.addEventListener('click', async () => {
          const productId = Number(button.dataset.productId);
          const product = rows.find((item) => Number(item.id) === productId);
          if (product) openProductModal(product);
        });
      });

      document.querySelectorAll('.delete-product').forEach((button) => {
        button.addEventListener('click', async () => {
          const productId = Number(button.dataset.productId);
          const confirmed = window.confirm('Delete this product from inventory?');
          if (!confirmed) return;
          try {
            await apiRequest(`${window.API_CONFIG.endpoints.products}/${productId}`, { method: 'DELETE' });
            await loadProducts();
          } catch (error) {
            console.error(error);
            alert('Unable to delete product.');
          }
        });
      });
    } catch (error) {
      console.error(error);
      productsTableBody.innerHTML = '<tr><td colspan="7">Unable to load products.</td></tr>';
    }
  }

  if (productsSearch) {
    productsSearch.addEventListener('input', loadProducts);
  }
  if (productsCategoryFilter) {
    productsCategoryFilter.addEventListener('change', loadProducts);
  }
  if (productsStatusFilter) {
    productsStatusFilter.addEventListener('change', loadProducts);
  }
  if (productsSortBy) {
    productsSortBy.addEventListener('change', loadProducts);
  }

  const productsAddBtn = document.getElementById('productsAddBtn');
  if (productsAddBtn) {
    productsAddBtn.addEventListener('click', () => openProductModal());
  }

  document.getElementById('productCloseBtn')?.addEventListener('click', closeProductModal);
  document.getElementById('productCancelBtn')?.addEventListener('click', closeProductModal);
  document.querySelector('[data-close-modal="true"]')?.addEventListener('click', closeProductModal);

  productForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(productForm);
    const payload = {
      name: formData.get('name')?.toString().trim(),
      sku: formData.get('sku')?.toString().trim() || '',
      category: formData.get('category')?.toString().trim(),
      status: formData.get('status')?.toString().trim() || 'active',
      price: Number(formData.get('price') || 0),
      cost_price: Number(formData.get('cost_price') || 0),
      stock: Number(formData.get('stock') || 0),
      min_stock: Number(formData.get('min_stock') || 0),
      description: formData.get('description')?.toString().trim() || '',
    };

    const productId = productForm.dataset.productId;
    const method = productId ? 'PUT' : 'POST';
    const endpoint = productId ? `${window.API_CONFIG.endpoints.products}/${productId}` : window.API_CONFIG.endpoints.products;

    try {
      await apiRequest(endpoint, {
        method,
        body: JSON.stringify(payload),
      });
      closeProductModal();
      await loadProducts();
    } catch (error) {
      console.error(error);
      alert(error.message || 'Unable to save product.');
    }
  });

  const customerPageState = {
    allCustomers: [],
    page: 1,
    perPage: 8,
  };

  function getCustomerStatusClass(status) {
    const normalized = String(status || 'Active').trim().toLowerCase();
    if (normalized === 'new') return 'status-new';
    if (normalized === 'inactive') return 'status-inactive';
    return 'status-active';
  }

  function getCustomerTypeClass(type) {
    const normalized = String(type || 'Regular').trim().toLowerCase();
    switch (normalized) {
      case 'vip': return 'customer-type-vip';
      case 'business': return 'customer-type-business';
      case 'premium': return 'customer-type-premium';
      default: return 'customer-type-regular';
    }
  }

  function openCustomerModal(mode = 'create', customer = null) {
    if (!customerModal || !customerForm) return;

    customerForm.reset();
    customerForm.dataset.customerId = customer ? customer.id : '';
    customerForm.dataset.mode = mode;
    customerFormTitle.textContent = mode === 'edit' ? 'Edit Customer' : mode === 'view' ? 'Customer Details' : 'Add Customer';

    const formInputs = customerForm.querySelectorAll('input, select, textarea');
    formInputs.forEach((input) => {
      const fieldName = input.name;
      if (!fieldName) return;
      if (fieldName === 'registration_date' && customer && customer.registration_date) {
        input.value = customer.registration_date;
      } else if (fieldName === 'customer_type' && customer) {
        input.value = customer.customer_type || 'Regular';
      } else if (fieldName === 'status' && customer) {
        input.value = customer.status || 'Active';
      } else if (customer && Object.prototype.hasOwnProperty.call(customer, fieldName)) {
        input.value = customer[fieldName] || '';
      }
    });

    const isReadOnly = mode === 'view';
    formInputs.forEach((input) => {
      input.disabled = isReadOnly;
      if (isReadOnly && input.name !== 'registration_date') {
        input.style.opacity = '0.9';
      }
    });

    const saveButton = customerForm.querySelector('button[type="submit"]');
    if (saveButton) {
      saveButton.style.display = isReadOnly ? 'none' : 'inline-flex';
    }

    customerModal.classList.remove('hidden');
    customerModal.setAttribute('aria-hidden', 'false');
  }

  function closeCustomerModal() {
    if (!customerModal || !customerForm) return;
    customerModal.classList.add('hidden');
    customerModal.setAttribute('aria-hidden', 'true');
    customerForm.reset();
    customerForm.dataset.customerId = '';
    customerForm.dataset.mode = 'create';
    customerFormMessage.textContent = '';
    customerForm.querySelectorAll('input, select, textarea').forEach((input) => {
      input.disabled = false;
      input.style.opacity = '1';
    });
    const saveButton = customerForm.querySelector('button[type="submit"]');
    if (saveButton) {
      saveButton.style.display = 'inline-flex';
    }
  }

  function renderCustomerSummary(stats) {
    if (!customersSummaryGrid) return;
    const cards = [
      { label: 'Total Customers', value: stats.total_customers || 0, sub: 'active CRM contacts' },
      { label: 'Active', value: stats.active_customers || 0, sub: 'currently engaged' },
      { label: 'Total Revenue', value: formatCurrency(stats.total_customer_revenue || 0), sub: 'all customer spend' },
      { label: 'Avg. Spend', value: formatCurrency(stats.average_customer_spend || 0), sub: 'per customer' },
      { label: 'VIP', value: stats.vip_customers || 0, sub: 'high-value segment' },
      { label: 'Business', value: stats.business_customers || 0, sub: 'corporate accounts' },
    ];
    customersSummaryGrid.innerHTML = cards.map((card) => `
      <div class="customer-summary-card">
        <div class="customer-summary-label">${card.label}</div>
        <div class="customer-summary-value">${card.value}</div>
        <div class="customer-summary-sub">${card.sub}</div>
      </div>
    `).join('');
  }

  function renderCustomerTable(rows) {
    if (!customersTableBody) return;

    if (!rows.length) {
      customersTableBody.innerHTML = '<tr><td colspan="8">No customer records match the current filters.</td></tr>';
      if (customersPagination) customersPagination.innerHTML = '';
      return;
    }

    const totalPages = Math.max(1, Math.ceil(rows.length / customerPageState.perPage));
    if (customerPageState.page > totalPages) {
      customerPageState.page = totalPages;
    }
    const start = (customerPageState.page - 1) * customerPageState.perPage;
    const paginatedRows = rows.slice(start, start + customerPageState.perPage);

    customersTableBody.innerHTML = paginatedRows.map((customer) => `
      <tr>
        <td>
          <div class="customer-name-cell">
            <div class="customer-avatar">${(customer.name || 'CU').split(' ').slice(0, 2).map((part) => part[0]).join('').toUpperCase()}</div>
            <div>
              <div class="customer-name">${customer.name || 'Unknown'}</div>
              <small>${customer.email || 'No email'}</small>
            </div>
          </div>
        </td>
        <td>
          <div class="customer-location">${customer.city || 'N/A'}, ${customer.state || 'N/A'}</div>
        </td>
        <td><span class="customer-type-badge ${getCustomerTypeClass(customer.customer_type)}">${customer.customer_type || 'Regular'}</span></td>
        <td><span class="customer-status-badge ${getCustomerStatusClass(customer.status)}">${customer.status || 'Active'}</span></td>
        <td>${customer.orders || 0}</td>
        <td>${formatCurrency(customer.total_spent || 0)}</td>
        <td>${customer.last_purchase || 'Never'}</td>
        <td>
          <div class="customer-action-cell">
            <button type="button" class="table-action-btn customer-view-btn" data-customer-id="${customer.id}">View</button>
            <button type="button" class="table-action-btn customer-edit-btn" data-customer-id="${customer.id}">Edit</button>
            <button type="button" class="table-action-btn danger customer-delete-btn" data-customer-id="${customer.id}">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');

    if (customersPagination) {
      const prevDisabled = customerPageState.page === 1 ? 'disabled' : '';
      const nextDisabled = customerPageState.page === totalPages ? 'disabled' : '';
      customersPagination.innerHTML = `
        <button type="button" class="pagination-btn" data-page="prev" ${prevDisabled}>Previous</button>
        <span>Page ${customerPageState.page} of ${totalPages}</span>
        <button type="button" class="pagination-btn" data-page="next" ${nextDisabled}>Next</button>
      `;

      customersPagination.querySelectorAll('.pagination-btn').forEach((button) => {
        button.addEventListener('click', () => {
          const pageAction = button.dataset.page;
          if (pageAction === 'prev' && customerPageState.page > 1) {
            customerPageState.page -= 1;
          }
          if (pageAction === 'next' && customerPageState.page < totalPages) {
            customerPageState.page += 1;
          }
          renderCustomerTable(getFilteredCustomerRows());
        });
      });
    }

    customersTableBody.querySelectorAll('.customer-view-btn').forEach((button) => {
      button.addEventListener('click', async () => {
        const customerId = Number(button.dataset.customerId);
        const customer = customerPageState.allCustomers.find((item) => item.id === customerId);
        if (!customer) return;
        openCustomerModal('view', customer);
        try {
          const saleResponse = await apiRequest(`${window.API_CONFIG.endpoints.customers}/${customerId}/sales`);
          const purchases = saleResponse.data || [];
          const historyList = purchases.length ? purchases.map((item) => `
            <li><span>${item.date}</span><strong>${item.product}</strong><em>${formatCurrency(item.total_amount)}</em></li>
          `).join('') : '<li class="history-empty">No purchases recorded yet.</li>';
          const historyContainer = customerForm.querySelector('.customer-history-list');
          if (historyContainer) historyContainer.innerHTML = historyList;
        } catch (error) {
          console.error(error);
        }
      });
    });

    customersTableBody.querySelectorAll('.customer-edit-btn').forEach((button) => {
      button.addEventListener('click', () => {
        const customerId = Number(button.dataset.customerId);
        const customer = customerPageState.allCustomers.find((item) => item.id === customerId);
        if (customer) openCustomerModal('edit', customer);
      });
    });

    customersTableBody.querySelectorAll('.customer-delete-btn').forEach((button) => {
      button.addEventListener('click', async () => {
        const customerId = Number(button.dataset.customerId);
        const customer = customerPageState.allCustomers.find((item) => item.id === customerId);
        if (!customer) return;
        const confirmed = window.confirm(`Delete customer ${customer.name}? This action cannot be undone.`);
        if (!confirmed) return;
        try {
          await apiRequest(`${window.API_CONFIG.endpoints.customers}/${customerId}`, { method: 'DELETE' });
          await loadCustomers();
        } catch (error) {
          console.error(error);
          alert(error.message || 'Unable to delete customer.');
        }
      });
    });
  }

  function getFilteredCustomerRows() {
    const searchValue = (customersSearch?.value || '').toLowerCase().trim();
    const typeValue = customersTypeFilter?.value || '';
    const statusValue = customersStatusFilter?.value || '';

    return customerPageState.allCustomers.filter((customer) => {
      const matchesSearch = !searchValue || [customer.name, customer.email, customer.city, customer.state, customer.customer_id].join(' ').toLowerCase().includes(searchValue);
      const matchesType = !typeValue || String(customer.customer_type || 'Regular') === typeValue;
      const matchesStatus = !statusValue || String(customer.status || 'Active') === statusValue;
      return matchesSearch && matchesType && matchesStatus;
    }).sort((left, right) => {
      const sortByValue = customersSortBy?.value || 'name';
      if (sortByValue === 'total_spent') {
        return Number(right.total_spent || 0) - Number(left.total_spent || 0);
      }
      if (sortByValue === 'orders') {
        return Number(right.orders || 0) - Number(left.orders || 0);
      }
      if (sortByValue === 'last_purchase') {
        const leftTime = new Date(left.last_purchase || '1970-01-01').getTime();
        const rightTime = new Date(right.last_purchase || '1970-01-01').getTime();
        return rightTime - leftTime;
      }
      return String(left.name || '').localeCompare(String(right.name || ''));
    });
  }

  async function loadCustomers() {
    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.customers);
      const rows = response.data || [];
      const stats = response.stats || {};
      customerPageState.allCustomers = rows;
      renderCustomerSummary(stats);
      renderCustomerTable(getFilteredCustomerRows());
    } catch (error) {
      console.error(error);
      customersSummaryGrid.innerHTML = '<div class="customer-summary-card"><div class="customer-summary-value">Unable to load customers</div></div>';
      customersTableBody.innerHTML = '<tr><td colspan="8">Unable to load customers.</td></tr>';
    }
  }

  async function loadReports() {
    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.reports);
      const rows = response.data || [];
      if (!rows.length) {
        reportsTableBody.innerHTML = '<tr><td colspan="6">No sales data available</td></tr>';
        return;
      }
      reportsTableBody.innerHTML = rows.map((row) => `
        <tr>
          <td>${row.id}</td>
          <td>${row.date}</td>
          <td>${row.product}</td>
          <td>${row.customer}</td>
          <td>${row.region}</td>
          <td>${formatCurrency(row.total_amount)}</td>
        </tr>
      `).join('');
    } catch (error) {
      console.error(error);
      reportsTableBody.innerHTML = '<tr><td colspan="6">Unable to load reports.</td></tr>';
    }
  }

  async function loadSalesHistory() {
    try {
      const search = document.getElementById('historySearch').value;
      const category = document.getElementById('historyCategoryFilter').value;
      const startDate = document.getElementById('historyStartDate').value;
      const endDate = document.getElementById('historyEndDate').value;
      const sortBy = document.getElementById('historySortBy').value;
      const order = document.getElementById('historyOrder').value;
      const params = new URLSearchParams({ search, category, start_date: startDate, end_date: endDate, sort_by: sortBy, order });
      const response = await apiRequest(`${window.API_CONFIG.endpoints.sales}?${params.toString()}`);
      const rows = response.data || [];
      if (!rows.length) {
        historyTableBody.innerHTML = '<tr><td colspan="7">No sales data available</td></tr>';
        return;
      }
      historyTableBody.innerHTML = rows.map((row) => `
        <tr>
          <td>${row.date}</td>
          <td>${row.product}</td>
          <td>${row.category}</td>
          <td>${row.customer}</td>
          <td>${row.region}</td>
          <td>${formatCurrency(row.total_amount)}</td>
          <td><button type="button" data-sale-id="${row.id}" class="delete-sale-button">Delete</button></td>
        </tr>
      `).join('');

      document.querySelectorAll('.delete-sale-button').forEach((button) => {
        button.addEventListener('click', async () => {
          const saleId = button.dataset.saleId;
          try {
            await apiRequest(`${window.API_CONFIG.endpoints.sales}/${saleId}`, { method: 'DELETE' });
            await loadSalesHistory();
          } catch (error) {
            console.error(error);
            alert('Unable to delete the selected sale.');
          }
        });
      });
    } catch (error) {
      console.error(error);
      historyTableBody.innerHTML = '<tr><td colspan="7">Unable to load sales history.</td></tr>';
    }
  }

  async function loadFilterOptions() {
    try {
      const categoriesResponse = await apiRequest(window.API_CONFIG.endpoints.categories);
      const categories = categoriesResponse.data || [];
      const categoryOptions = ['<option value="">All categories</option>']
        .concat(categories.map((category) => `<option value="${category}">${category}</option>`))
        .join('');
      historyCategoryFilter.innerHTML = categoryOptions;
      analysisCategory.innerHTML = categoryOptions;

      const salesResponse = await apiRequest(`${window.API_CONFIG.endpoints.sales}?sort_by=date&order=desc`);
      const sales = salesResponse.data || [];
      const regions = [...new Set(sales.map((sale) => sale.region).filter(Boolean))];
      analysisRegion.innerHTML = ['<option value="">All regions</option>']
        .concat(regions.map((region) => `<option value="${region}">${region}</option>`))
        .join('');

      const paymentMethods = [...new Set(sales.map((sale) => sale.payment_method).filter(Boolean))];
      analysisPaymentMethod.innerHTML = ['<option value="">All payment methods</option>']
        .concat(paymentMethods.map((method) => `<option value="${method}">${method}</option>`))
        .join('');
    } catch (error) {
      console.error(error);
    }
  }

  async function loadAnalysis() {
    const rangeButton = document.querySelector('.analysis-range-btn.active');
    const selectedRange = rangeButton ? rangeButton.dataset.range : 'all';
    const params = new URLSearchParams();
    const startDate = analysisStartDate ? analysisStartDate.value : '';
    const endDate = analysisEndDate ? analysisEndDate.value : '';
    const category = analysisCategory ? analysisCategory.value : '';
    const region = analysisRegion ? analysisRegion.value : '';
    const paymentMethod = analysisPaymentMethod ? analysisPaymentMethod.value : '';

    if (selectedRange && selectedRange !== 'all') params.append('range', selectedRange);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (category) params.append('category', category);
    if (region) params.append('region', region);
    if (paymentMethod) params.append('payment_method', paymentMethod);

    try {
      const response = await apiRequest(`${window.API_CONFIG.endpoints.analysis}?${params.toString()}`);
      const data = response.data || {};
      const summary = data.summary || {};
      const summaryGrid = document.getElementById('analysisSummary');

      if (!data || Object.keys(data).length === 0 || !summary || Object.keys(summary).length === 0) {
        summaryGrid.innerHTML = '<div class="summary-card"><div class="label">Analysis</div><div class="value">No sales data available</div></div>';
        analysisStatus.textContent = 'No sales data available for the selected period.';
        return;
      }

      summaryGrid.innerHTML = [
        renderMetricCard('Total Sales', formatCurrency(summary.total_revenue || 0)),
        renderMetricCard('Total Orders', summary.total_orders || 0),
        renderMetricCard('Units Sold', summary.units_sold || 0),
        renderMetricCard('Total Profit', formatCurrency(summary.total_profit || 0)),
        renderMetricCard('Average Order Value', formatCurrency(summary.average_order_value || 0)),
        renderMetricCard('Profit Margin', `${Number(summary.profit_margin || 0).toFixed(1)}%`),
      ].join('');

      analysisStatus.textContent = `${summary.total_orders || 0} orders in scope`;
      analysisStatus.classList.remove('error');

      renderLineChart('analysisMonthlyChart', data.sales_by_month || [], 'month', 'total', (value) => formatCurrency(value), '#16a34a');
      renderVerticalBarChart('analysisCategoryChart', data.sales_by_category || [], 'category', 'total', (value) => formatCurrency(value), 'value', '#16a34a');
      renderHorizontalBarChart('analysisRegionChart', data.sales_by_region || [], 'region', 'total', (value) => formatCurrency(value), '#16a34a');
      renderHorizontalBarChart('analysisProductsChart', data.top_products || [], 'product', 'revenue', (value) => formatCurrency(value), '#16a34a');
      renderLineChart('analysisProfitChart', data.profit_by_month || [], 'month', 'profit', (value) => formatCurrency(value), '#16a34a');
      renderScatterChart('analysisScatterChart', data.sales_vs_profit || [], '#16a34a');
      renderVerticalBarChart('analysisMarginChart', data.profit_margin_by_category || [], 'category', 'margin', (value) => `${Number(value).toFixed(1)}%`, 'margin', '#16a34a');
      renderComparisonPanel('analysisComparison', data.performance_comparison || { current: {}, previous: {}, change: {} });
      renderInsightsPanel('analysisInsights', data.business_insights || []);
      renderPerformerMatrix('analysisPerformers', data.best_worst_performers || {});
    } catch (error) {
      console.error(error);
      analysisStatus.textContent = 'Unable to load analysis data. Please retry.';
      analysisStatus.classList.add('error');
      document.getElementById('analysisSummary').innerHTML = '<div class="summary-card"><div class="label">Analysis</div><div class="value">Unable to load analysis.</div></div>';
    }
  }

  saleForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearError(saleSuccessMessage);
    const payload = {
      date: document.getElementById('saleDate').value,
      product: document.getElementById('saleProduct').value,
      category: document.getElementById('saleCategory').value,
      quantity: Number(document.getElementById('saleQuantity').value),
      unit_price: Number(document.getElementById('saleUnitPrice').value),
      discount: Number(document.getElementById('saleDiscount').value || 0),
      customer: document.getElementById('saleCustomer').value,
      region: document.getElementById('saleRegion').value,
      payment_method: document.getElementById('salePaymentMethod').value,
    };

    try {
      await apiRequest(window.API_CONFIG.endpoints.sales, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      saleSuccessMessage.textContent = 'Sale saved successfully.';
      saleSuccessMessage.classList.remove('error');
      saleForm.reset();
      await Promise.all([loadDashboard(), loadProducts(), loadCustomers(), loadReports(), loadSalesHistory(), loadFilterOptions()]);
    } catch (error) {
      setError(saleSuccessMessage, error.message);
    }
  });

  predictionForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearError(predictionResult);
    const payload = {
      product: document.getElementById('predProduct').value,
      category: document.getElementById('predCategory').value,
      quantity: Number(document.getElementById('predQuantity').value),
      unit_price: Number(document.getElementById('predUnitPrice').value),
      discount: Number(document.getElementById('predDiscount').value || 0),
      customer: document.getElementById('predCustomer').value,
      region: document.getElementById('predRegion').value,
      payment_method: document.getElementById('predPaymentMethod').value,
      date: new Date().toISOString().slice(0, 10),
    };

    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.predict, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      const data = response.prediction || {};
      predictionResult.textContent = `Predicted total amount: ${formatCurrency(data.predicted_total_amount || 0)}`;
      predictionResult.classList.remove('error');
    } catch (error) {
      setError(predictionResult, error.message);
    }
  });

  document.querySelectorAll('.analysis-range-btn').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.analysis-range-btn').forEach((item) => item.classList.toggle('active', item === button));
      loadAnalysis();
    });
  });

  if (analysisResetBtn) {
    analysisResetBtn.addEventListener('click', () => {
      if (analysisStartDate) analysisStartDate.value = '';
      if (analysisEndDate) analysisEndDate.value = '';
      if (analysisCategory) analysisCategory.value = '';
      if (analysisRegion) analysisRegion.value = '';
      if (analysisPaymentMethod) analysisPaymentMethod.value = '';
      document.querySelectorAll('.analysis-range-btn').forEach((button) => {
        button.classList.toggle('active', button.dataset.range === 'all');
      });
      loadAnalysis();
    });
  }

  analysisFilterForm.addEventListener('submit', (event) => {
    event.preventDefault();
    loadAnalysis();
  });

  if (customersSearch) customersSearch.addEventListener('input', () => {
    customerPageState.page = 1;
    renderCustomerTable(getFilteredCustomerRows());
  });
  if (customersTypeFilter) customersTypeFilter.addEventListener('change', () => {
    customerPageState.page = 1;
    renderCustomerTable(getFilteredCustomerRows());
  });
  if (customersStatusFilter) customersStatusFilter.addEventListener('change', () => {
    customerPageState.page = 1;
    renderCustomerTable(getFilteredCustomerRows());
  });
  if (customersSortBy) customersSortBy.addEventListener('change', () => {
    customerPageState.page = 1;
    renderCustomerTable(getFilteredCustomerRows());
  });

  const customersAddBtn = document.getElementById('customersAddBtn');
  if (customersAddBtn) {
    customersAddBtn.addEventListener('click', () => openCustomerModal('create'));
  }

  const customerCloseButtons = document.querySelectorAll('[data-close-customer-modal="true"]');
  customerCloseButtons.forEach((button) => button.addEventListener('click', closeCustomerModal));

  customerForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(customerForm).entries());
    const method = customerForm.dataset.customerId ? 'PUT' : 'POST';
    const endpoint = customerForm.dataset.customerId ? `${window.API_CONFIG.endpoints.customers}/${customerForm.dataset.customerId}` : window.API_CONFIG.endpoints.customers;

    try {
      customerFormMessage.textContent = 'Saving customer...';
      customerFormMessage.classList.remove('error');
      await apiRequest(endpoint, {
        method,
        body: JSON.stringify(payload),
      });
      closeCustomerModal();
      await loadCustomers();
    } catch (error) {
      console.error(error);
      customerFormMessage.textContent = error.message || 'Unable to save customer details.';
      customerFormMessage.classList.add('error');
    }
  });

  document.getElementById('historySearch').addEventListener('input', loadSalesHistory);
  document.getElementById('historyCategoryFilter').addEventListener('change', loadSalesHistory);
  document.getElementById('historyStartDate').addEventListener('change', loadSalesHistory);
  document.getElementById('historyEndDate').addEventListener('change', loadSalesHistory);
  document.getElementById('historySortBy').addEventListener('change', loadSalesHistory);
  document.getElementById('historyOrder').addEventListener('change', loadSalesHistory);

  document.getElementById('downloadCsvBtn').addEventListener('click', async () => {
    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.reports);
      const rows = response.data || [];
      const csv = [
        ['id', 'date', 'product', 'category', 'quantity', 'unit_price', 'discount', 'customer', 'region', 'payment_method', 'total_amount'],
        ...rows.map((row) => [row.id, row.date, row.product, row.category, row.quantity, row.unit_price, row.discount, row.customer, row.region, row.payment_method, row.total_amount]),
      ].map((line) => line.map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'sales_report.csv';
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert('Unable to export CSV.');
    }
  });

  document.getElementById('downloadExcelBtn').addEventListener('click', async () => {
    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.reports);
      const rows = response.data || [];
      if (!rows.length) {
        alert('No sales data available to export.');
        return;
      }
      const csv = [
        ['id', 'date', 'product', 'category', 'quantity', 'unit_price', 'discount', 'customer', 'region', 'payment_method', 'total_amount'],
        ...rows.map((row) => [row.id, row.date, row.product, row.category, row.quantity, row.unit_price, row.discount, row.customer, row.region, row.payment_method, row.total_amount]),
      ].map((line) => line.map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
      const blob = new Blob([csv], { type: 'application/vnd.ms-excel' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'sales_report.xls';
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert('Unable to export Excel data.');
    }
  });

  async function loadDatabaseStatus() {
    try {
      const response = await apiRequest(window.API_CONFIG.endpoints.health);
      dbStatus.textContent = `Database ready • ${response.records} records`;
    } catch (error) {
      dbStatus.textContent = 'Database unavailable';
      dbStatus.classList.add('error');
      console.error(error);
    }
  }

  loadDashboard();
  loadProducts();
  loadCustomers();
  loadReports();
  loadSalesHistory();
  loadFilterOptions();
  loadAnalysis();
  loadDatabaseStatus();
});
