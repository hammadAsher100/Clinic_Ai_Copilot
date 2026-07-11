/**
 * Clinical AI Co-Pilot — Chart Utilities
 *
 * Vanilla Canvas-based charts for SHAP bar charts and confidence gauges.
 * No external chart library dependency.
 */

/**
 * Render a horizontal bar chart of SHAP values.
 * @param {string} containerId - DOM element ID to render into
 * @param {Object} shapValues  - {featureName: shapValue, ...}
 */
function renderSHAPChart(containerId, shapValues) {
  const container = document.getElementById(containerId);
  if (!container || !shapValues) return;

  // Sort by absolute value, take top 10
  const sorted = Object.entries(shapValues)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 10);

  if (sorted.length === 0) {
    container.innerHTML = '<p class="text-muted">No SHAP values available</p>';
    return;
  }

  const maxAbs = Math.max(...sorted.map(([, v]) => Math.abs(v)));

  let html = '<div style="font-size: 0.8rem;">';
  for (const [name, value] of sorted) {
    const width = Math.max(5, (Math.abs(value) / maxAbs) * 100);
    const color = value > 0 ? 'var(--accent-coral)' : 'var(--accent-teal)';
    const label = name.length > 20 ? name.substring(0, 18) + '…' : name;

    html += `
      <div style="display:flex;align-items:center;margin-bottom:6px;gap:8px;">
        <span style="width:120px;text-align:right;color:var(--text-secondary);flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${name}">${label}</span>
        <div style="flex:1;height:18px;background:var(--bg-primary);border-radius:4px;overflow:hidden;position:relative;">
          <div style="width:${width}%;height:100%;background:${color};border-radius:4px;transition:width 0.8s cubic-bezier(0.4,0,0.2,1);"></div>
        </div>
        <span style="width:60px;font-size:0.75rem;color:var(--text-muted);text-align:right;">${value > 0 ? '+' : ''}${value.toFixed(3)}</span>
      </div>`;
  }
  html += '</div>';

  container.innerHTML = html;
}


/**
 * Render a confidence gauge (semicircle arc).
 * @param {string} containerId - DOM element ID
 * @param {number} confidence  - 0 to 1
 * @param {string} label       - prediction label
 */
function renderConfidenceGauge(containerId, confidence, label) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const pct = Math.round(confidence * 100);
  const color = confidence >= 0.8 ? 'var(--accent-teal)'
    : confidence >= 0.5 ? 'var(--accent-amber)'
    : 'var(--accent-coral)';

  container.innerHTML = `
    <div style="text-align:center;">
      <div style="position:relative;width:120px;height:60px;margin:0 auto;">
        <svg viewBox="0 0 120 60" style="width:120px;height:60px;">
          <path d="M 10 55 A 50 50 0 0 1 110 55" fill="none" stroke="var(--bg-primary)" stroke-width="8" stroke-linecap="round"/>
          <path d="M 10 55 A 50 50 0 0 1 110 55" fill="none" stroke="${color}" stroke-width="8" stroke-linecap="round"
            stroke-dasharray="${confidence * 157} 157" style="transition:stroke-dasharray 1s cubic-bezier(0.4,0,0.2,1);"/>
        </svg>
        <div style="position:absolute;bottom:0;left:50%;transform:translateX(-50%);font-size:1.5rem;font-weight:800;color:${color};">${pct}%</div>
      </div>
      ${label ? `<div style="margin-top:6px;font-size:0.8rem;color:var(--text-secondary);">${label}</div>` : ''}
    </div>`;
}


/**
 * Render top-3 conditions as styled list items.
 * @param {string} containerId
 * @param {Array} top3 - [{condition, confidence}, ...]
 */
function renderTop3Conditions(containerId, top3) {
  const container = document.getElementById(containerId);
  if (!container || !top3 || !top3.length) return;

  let html = '';
  const colors = ['var(--accent-teal)', 'var(--accent-blue)', 'var(--accent-purple)'];

  top3.forEach((item, i) => {
    const pct = Math.round(item.confidence * 100);
    html += `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <span style="width:24px;height:24px;border-radius:50%;background:${colors[i]};display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:700;color:var(--bg-deep);flex-shrink:0;">${i + 1}</span>
        <div style="flex:1;">
          <div style="font-size:0.85rem;font-weight:600;color:var(--text-primary);">${item.condition}</div>
          <div class="progress-bar" style="height:6px;margin:3px 0 0;">
            <div class="fill" style="width:${pct}%;background:${colors[i]};"></div>
          </div>
        </div>
        <span style="font-size:0.8rem;font-weight:600;color:${colors[i]};">${pct}%</span>
      </div>`;
  });

  container.innerHTML = html;
}
