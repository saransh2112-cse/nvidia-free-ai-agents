const scanBtn = document.getElementById('scan-btn');
const clearBtn = document.getElementById('clear-btn');
const codeInput = document.getElementById('code-input');
const terminal = document.getElementById('terminal');
const status = document.getElementById('agent-status');
const diagnostics = document.getElementById('diagnostics');
const healedView = document.getElementById('healed-view');
const healedCode = document.getElementById('healed-code');
const issueCount = document.getElementById('issue-count');

function addTerm(msg, type = 'SYSTEM') {
    const line = document.createElement('div');
    line.className = 'term-line';
    const now = new Date().toLocaleTimeString([], { hour12: false });
    line.innerHTML = `<span>[${now}]</span> [${type}] ${msg}`;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

function updateStatus(text, active = false) {
    status.textContent = `AGENT STATUS: ${text}`;
    status.style.textShadow = active ? '0 0 15px var(--accent)' : 'none';
    status.style.color = active ? 'var(--accent)' : '#555';
}

scanBtn.addEventListener('click', async () => {
    const code = codeInput.value.trim();
    if (!code) return addTerm("ABORT: No source code detected.", "ERROR");

    scanBtn.disabled = true;
    updateStatus("SCANNING NEURAL PATHWAYS...", true);
    addTerm("Initializing Deep Intelligence Scan...", "SCOUT");
    addTerm("Target: meta/llama-3.1-8b-instruct", "NVIDIA-NIM");
    
    diagnostics.innerHTML = '<div style="text-align: center; color: var(--accent); margin-top: 50px; animation: pulse 1s infinite;">ANALYZING VULNERABILITIES...</div>';
    healedView.style.display = 'none';

    try {
        const response = await fetch('/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.error) throw new Error(data.error);

        addTerm(`Scan Complete. ${data.issues.length} vulnerabilities isolated.`, "SUCCESS");
        updateStatus("REFACTORING COMPLETE", false);
        
        issueCount.textContent = `${data.issues.length} Issues Detected`;
        diagnostics.innerHTML = '';
        
        data.issues.forEach(issue => {
            const card = document.createElement('div');
            card.className = `issue-card ${issue.severity}`;
            card.innerHTML = `
                <div class="issue-type">${issue.severity.toUpperCase()} | ${issue.type}</div>
                <div class="issue-desc">${issue.desc}</div>
                <div class="diff-link">VIEW HEALED BLOCK</div>
            `;
            
            card.querySelector('.diff-link').addEventListener('click', () => {
                addTerm(`Inspecting Refactored Block: ${issue.type}`, "VIEWER");
                alert(`ORIGINAL:\n${issue.original}\n\nFIXED:\n${issue.fixed}`);
            });
            
            diagnostics.appendChild(card);
        });

        // Show the full healed code
        healedView.style.display = 'block';
        healedCode.textContent = data.healed_code;
        addTerm("Full Healed Payload projected below.", "SYSTEM");

    } catch (err) {
        addTerm(`CRITICAL FAILURE: ${err.message}`, "ERROR");
        updateStatus("EMERGENCY SHUTDOWN", false);
    } finally {
        scanBtn.disabled = false;
    }
});

clearBtn.addEventListener('click', () => {
    codeInput.value = '';
    diagnostics.innerHTML = '<div style="text-align: center; color: #555; margin-top: 100px;">Waiting for code injection...</div>';
    healedView.style.display = 'none';
    issueCount.textContent = '0 Issues';
    addTerm("Workspace purged.", "SYSTEM");
});

// Matrix Background Effect
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
document.getElementById('matrix').appendChild(canvas);
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#@&*%';
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);

function drawMatrix() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0f0';
    ctx.font = fontSize + 'px monospace';
    for (let i = 0; i < drops.length; i++) {
        const text = chars.charAt(Math.floor(Math.random() * chars.length));
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(drawMatrix, 50);
