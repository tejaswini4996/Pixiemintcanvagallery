// Delivery Tracker Controller
function trackOrder() {
  const input = document.getElementById('trackInput');
  const resultContainer = document.getElementById('trackingResult');
  if (!input || !resultContainer) return;

  const orderId = input.value.trim();
  if (!orderId) {
    alert("Please enter a valid Order ID");
    return;
  }

  resultContainer.innerHTML = '<div style="color: var(--accent-mint-light); text-align: center; padding: 2rem;">Fetching canvas delivery status...</div>';

  fetch(`/api/track/${orderId}`)
    .then(res => res.json())
    .then(data => {
      if (data.status === 'error') {
        resultContainer.innerHTML = `<div style="color: #ef4444; padding: 1.5rem; background: rgba(239, 68, 68, 0.1); border-radius: var(--radius-md); text-align: center;">${data.message}</div>`;
        return;
      }

      const info = data.tracking;
      let html = `
        <div style="background: rgba(255, 255, 255, 0.03); padding: 1.2rem; border-radius: var(--radius-md); margin-bottom: 2rem; border: 1px solid var(--border-color);">
          <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
              <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Customer</div>
              <div style="font-weight: 700;">${info.customer_name} (${info.city})</div>
            </div>
            <div>
              <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Tracking Number</div>
              <div style="font-weight: 700; color: var(--accent-gold);">${info.tracking_number}</div>
            </div>
            <div>
              <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Carrier</div>
              <div style="font-weight: 700; color: var(--accent-mint-light);">${info.carrier}</div>
            </div>
          </div>
        </div>
      `;

      info.stages.forEach(stage => {
        const cls = stage.status;
        const icon = stage.status === 'completed' ? '✓' : (stage.status === 'active' ? '●' : '○');
        html += `
          <div class="timeline-step ${cls}">
            <div class="step-marker">${icon}</div>
            <div class="step-details">
              <h4>${stage.title}</h4>
              <p>${stage.desc}</p>
            </div>
          </div>
        `;
      });

      resultContainer.innerHTML = html;
    })
    .catch(err => {
      resultContainer.innerHTML = '<div style="color: #ef4444;">Error retrieving tracking data. Please try again.</div>';
    });
}

// Auto load sample order tracking on page load
document.addEventListener('DOMContentLoaded', () => {
  trackOrder();
});
