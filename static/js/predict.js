// Optional: use fetch to call /api/predict with JSON
async function apiPredict(payload) {
  const res = await fetch('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return await res.json();
}

// Example usage (uncomment to enable button-driven AJAX)
// document.getElementById('predictBtn').addEventListener('click', async () => {
//   const payload = { Quantity: 1, 'Unit Price': 49, Discount: 0.05, Category: 'Electronics', Region: 'North', 'Payment Method': 'Credit Card' };
//   const result = await apiPredict(payload);
//   console.log(result);
// });
