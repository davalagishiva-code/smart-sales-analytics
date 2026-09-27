const API_CONFIG = {
  baseUrl: 'http://127.0.0.1:8080',
  endpoints: {
    dashboard: '/api/dashboard',
    analysis: '/api/analysis',
    sales: '/api/sales',
    categories: '/api/categories',
    products: '/api/products',
    customers: '/api/customers',
    predict: '/api/predict',
    reports: '/api/reports',
    health: '/health',
  },
};

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_CONFIG.baseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = 'Unknown API error';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || JSON.stringify(errorJson);
    } catch (err) {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail);
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  return response.text();
}

window.API_CONFIG = API_CONFIG;
window.apiRequest = apiRequest;
