// Unibot Web Dashboard Controller

let state = {
    aim: false,
    trigger: false,
    rapid_fire: false,
    recoil: false
};

let config = {};

// Color presets (HSV values for common games)
const COLOR_PRESETS = {
    valorant: { lower: [50, 100, 100], upper: [80, 255, 255], name: 'Valorant (Yellow)' },
    overwatch: { lower: [100, 100, 100], upper: [130, 255, 255], name: 'Overwatch (Blue)' },
    csgo: { lower: [35, 100, 100], upper: [85, 255, 255], name: 'CS:GO (Green)' },
    apex: { lower: [0, 100, 100], upper: [30, 255, 255], name: 'Apex (Red/Orange)' },
    destiny2: { lower: [200, 100, 100], upper: [230, 255, 255], name: 'Destiny 2 (Purple)' }
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    setLocalIP();
    loadConfig();
    initColorPreview();
    pollState();
    setInterval(pollState, 1000);  // Poll state every second
});

function setLocalIP() {
    fetch('/api/state').then(() => {
        const hostname = window.location.hostname;
        const port = window.location.port || '5000';
        document.getElementById('local-ip').textContent = `http://${hostname}:${port}`;
    });
}

function pollState() {
    fetch('/api/state')
        .then(r => r.json())
        .then(data => {
            updateStatusDisplay(data);
        })
        .catch(e => console.error('State poll failed:', e));
}

function updateStatusDisplay(data) {
    // Update status lights
    updateStatusLight('aim-btn', data.aim_enabled);
    updateStatusLight('trigger-btn', data.trigger_enabled);
    updateStatusLight('rapid-btn', data.rapid_fire_enabled);
    updateStatusLight('recoil-btn', data.recoil_enabled);

    // Update target status
    const targetStatus = document.getElementById('target-status');
    if (data.target_detected) {
        targetStatus.textContent = '✅ Locked';
        targetStatus.style.color = '#00ff00';
    } else {
        targetStatus.textContent = '❌ None';
        targetStatus.style.color = '#ff6666';
    }

    // Update pose
    document.getElementById('pose-status').textContent = data.detected_pose;

    // Update FPS
    document.getElementById('fps-status').textContent = Math.round(data.fps);
}

function updateStatusLight(btnId, enabled) {
    const btn = document.getElementById(btnId);
    const light = btn.querySelector('.status-light');

    if (enabled) {
        btn.classList.add('active');
        light.classList.add('on');
        light.classList.remove('off');
    } else {
        btn.classList.remove('active');
        light.classList.remove('on');
        light.classList.add('off');
    }
}

function toggleControl(action) {
    const actionMap = {
        'aim': 'toggle_aim',
        'trigger': 'toggle_trigger',
        'rapid_fire': 'toggle_rapid_fire',
        'recoil': 'toggle_recoil'
    };

    fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionMap[action] })
    })
        .then(r => r.json())
        .then(data => {
            state[action] = data.state[action + '_enabled'];
            updateStatusDisplay(data.state);
        })
        .catch(e => console.error('Control failed:', e));
}

function loadConfig() {
    fetch('/api/config')
        .then(r => r.json())
        .then(data => {
            config = data;
            populateConfigUI(data);
        })
        .catch(e => console.error('Config load failed:', e));
}

function populateConfigUI(config) {
    // Aim tab
    document.getElementById('aim-speed').value = config.aim.speed;
    document.getElementById('aim-speed-val').textContent = config.aim.speed.toFixed(1);

    document.getElementById('aim-smooth').value = config.aim.smoothing;
    document.getElementById('aim-smooth-val').textContent = config.aim.smoothing.toFixed(1);

    document.getElementById('aim-y-mult').value = config.aim.y_multiplier;
    document.getElementById('aim-y-mult-val').textContent = config.aim.y_multiplier.toFixed(1);

    // Trigger tab
    document.getElementById('trigger-delay').value = config.trigger.delay;
    document.getElementById('trigger-threshold').value = config.trigger.threshold;

    // Shape tab
    document.getElementById('shape-aspect-min').value = config.shape_validation.aspect_ratio_min;
    document.getElementById('shape-convexity').value = config.shape_validation.min_convexity;

    // Pose tab
    document.getElementById('pose-standing').value = config.pose_detection.standing_threshold;
    document.getElementById('pose-crouch').value = config.pose_detection.crouching_threshold;

    // Add value sync listeners
    document.getElementById('aim-speed').addEventListener('input', (e) => {
        document.getElementById('aim-speed-val').textContent = e.target.value;
    });
    document.getElementById('aim-smooth').addEventListener('input', (e) => {
        document.getElementById('aim-smooth-val').textContent = e.target.value;
    });
    document.getElementById('aim-y-mult').addEventListener('input', (e) => {
        document.getElementById('aim-y-mult-val').textContent = e.target.value;
    });
}

function switchTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabId).classList.add('active');

    // Activate button
    event.target.classList.add('active');
}

// Color Preview System
function initColorPreview() {
    const canvas = document.getElementById('preview-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Draw gradient for visual reference
    drawColorGradient(ctx);

    // Load current HSV values if available
    if (config && config.screen) {
        const lower = config.screen.lower_color || [58, 210, 80];
        const upper = config.screen.upper_color || [63, 255, 255];
        updateColorInputs(lower, upper);
    }
}

function drawColorGradient(ctx) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;

    // Draw HSV color wheel (simplified)
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const h = (x / width) * 180;  // Hue (0-180 in OpenCV HSV)
            const s = (y / height) * 255;  // Saturation
            const v = 200;  // Value (brightness)

            const rgb = hsvToRgb(h, s, v);
            ctx.fillStyle = `rgb(${rgb.r},${rgb.g},${rgb.b})`;
            ctx.fillRect(x, y, 1, 1);
        }
    }

    // Draw selection box (if color bounds available)
    updateColorPreviewBox();
}

function updateColorPreview() {
    const canvas = document.getElementById('preview-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    drawColorGradient(ctx);

    // Redraw with new bounds
    updateColorPreviewBox();

    // Update config
    const lower = [
        parseInt(document.getElementById('lower-h').value) || 58,
        parseInt(document.getElementById('lower-s').value) || 210,
        parseInt(document.getElementById('lower-v').value) || 80
    ];
    const upper = [
        parseInt(document.getElementById('upper-h').value) || 63,
        parseInt(document.getElementById('upper-s').value) || 255,
        parseInt(document.getElementById('upper-v').value) || 255
    ];

    // Send to server
    updateConfig('screen', 'lower_color', lower.join(','));
    updateConfig('screen', 'upper_color', upper.join(','));
}

function updateColorPreviewBox() {
    const canvas = document.getElementById('preview-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const lowerH = parseInt(document.getElementById('lower-h').value) || 58;
    const upperH = parseInt(document.getElementById('upper-h').value) || 63;
    const lowerS = parseInt(document.getElementById('lower-s').value) || 210;
    const upperS = parseInt(document.getElementById('upper-s').value) || 255;

    // Draw selection box
    const xStart = (lowerH / 180) * width;
    const xEnd = (upperH / 180) * width;
    const yStart = (lowerS / 255) * height;
    const yEnd = (upperS / 255) * height;

    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.strokeRect(xStart, yStart, xEnd - xStart, yEnd - yStart);

    ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
    ctx.fillRect(xStart, yStart, xEnd - xStart, yEnd - yStart);
}

function updateColorInputs(lower, upper) {
    document.getElementById('lower-h').value = lower[0];
    document.getElementById('lower-s').value = lower[1];
    document.getElementById('lower-v').value = lower[2];

    document.getElementById('upper-h').value = upper[0];
    document.getElementById('upper-s').value = upper[1];
    document.getElementById('upper-v').value = upper[2];
}

function presetColor(presetName) {
    const preset = COLOR_PRESETS[presetName];
    if (!preset) return;

    updateColorInputs(preset.lower, preset.upper);
    updateColorPreview();
}

// HSV to RGB conversion
function hsvToRgb(h, s, v) {
    h = h / 60;
    s = s / 255;
    v = v / 255;

    const c = v * s;
    const x = c * (1 - Math.abs((h % 2) - 1));
    const m = v - c;

    let r, g, b;
    if (h >= 0 && h < 1) { r = c; g = x; b = 0; }
    else if (h >= 1 && h < 2) { r = x; g = c; b = 0; }
    else if (h >= 2 && h < 3) { r = 0; g = c; b = x; }
    else if (h >= 3 && h < 4) { r = 0; g = x; b = c; }
    else if (h >= 4 && h < 5) { r = x; g = 0; b = c; }
    else { r = c; g = 0; b = x; }

    return {
        r: Math.round((r + m) * 255),
        g: Math.round((g + m) * 255),
        b: Math.round((b + m) * 255)
    };
}

function updateConfig(section, key, value) {
    fetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            section: section,
            key: key,
            value: value
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'ok') {
                console.log(`Updated ${key} to ${value}`);
            } else {
                console.error('Config update failed:', data.message);
            }
        })
        .catch(e => console.error('Config update failed:', e));
}
