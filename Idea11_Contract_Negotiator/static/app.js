const negotiateBtn = document.getElementById('negotiate-btn');
const contractInput = document.getElementById('contract-input');
const riskList = document.getElementById('risk-list');
const duelLog = document.getElementById('duel-log');
const scoreVal = document.getElementById('mitigation-score');
const gaugeFill = document.getElementById('gauge-fill');
const riskCountText = document.getElementById('risk-count');
const scanner = document.getElementById('scanner');

// Initialize Particles
particlesJS("particles-js", {
    particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: "#ffffff" },
        shape: { type: "circle" },
        opacity: { value: 0.2, random: false },
        size: { value: 2, random: true },
        line_linked: { enable: true, distance: 150, color: "#ffffff", opacity: 0.1, width: 1 },
        move: { enable: true, speed: 1, direction: "none", random: false, straight: false, out_mode: "out", bounce: false }
    },
    interactivity: { detect_on: "canvas", events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" }, resize: true } },
    retina_detect: true
});

async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function animateGauge(value) {
    const rotation = (value / 100) * 180 - 180;
    gaugeFill.style.transform = `rotate(${rotation}deg)`;
    
    let current = 0;
    const interval = setInterval(() => {
        if (current >= value) {
            clearInterval(interval);
            scoreVal.textContent = value.toFixed(1);
        } else {
            current += 1.5;
            scoreVal.textContent = current.toFixed(1);
        }
    }, 20);
}

async function typeText(element, text, speed = 10) {
    element.classList.add('typing');
    let currentText = "";
    for (let i = 0; i < text.length; i++) {
        currentText += text.charAt(i);
        element.textContent = currentText;
        if (i % 3 === 0) duelLog.scrollTop = duelLog.scrollHeight;
        await sleep(speed);
    }
    element.classList.remove('typing');
}

negotiateBtn.addEventListener('click', async () => {
    const text = contractInput.value.trim();
    if (!text) return alert("NO PAYLOAD DETECTED.");

    negotiateBtn.disabled = true;
    negotiateBtn.textContent = "INJECTING NEURAL SWARM...";
    
    // Start Laser Scanner
    scanner.style.display = 'block';
    scanner.style.animation = 'scan 2s infinite linear';
    
    riskList.innerHTML = '<div style="text-align: center; color: var(--gold); margin-top: 50px; font-weight: 900; animation: blink 0.5s infinite;">NEURAL AUDIT IN PROGRESS...</div>';
    duelLog.innerHTML = '<div style="text-align: center; color: var(--accent); margin-top: 50px; font-weight: 900; animation: blink 0.5s infinite;">CALCULATING STRATEGY...</div>';
    
    try {
        const res = await fetch('/negotiate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contract_text: text })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        // 1. Update Gauge
        animateGauge(data.score || 85);

        // 2. Stop Scanner
        scanner.style.display = 'none';

        // 3. Populate Risks
        riskList.innerHTML = '';
        riskCountText.textContent = `${data.risks.length} THREATS NEUTRALIZED`;
        data.risks.forEach((risk, i) => {
            setTimeout(() => {
                const card = document.createElement('div');
                card.className = 'risk-card';
                card.style.borderLeftColor = risk.risk_score > 70 ? 'var(--danger)' : 'var(--gold)';
                card.innerHTML = `
                    <div class="risk-name">${risk.clause_name}</div>
                    <div class="risk-desc">${risk.explanation}</div>
                `;
                riskList.appendChild(card);
            }, i * 200);
        });

        // 4. Animate Duel with Typing Effect
        duelLog.innerHTML = '';
        for (const neg of data.negotiations) {
            const separator = document.createElement('div');
            separator.style = 'font-size: 0.6rem; color: var(--gold); border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding: 5px 0; margin: 15px 0; text-transform: uppercase; font-weight: 900;';
            separator.textContent = `TARGET: ${neg.risk_name}`;
            duelLog.appendChild(separator);

            for (const msg of neg.duel_log) {
                const bubble = document.createElement('div');
                const isCloser = msg.agent.includes("Llama") || msg.agent.includes("Closer");
                bubble.className = `chat-bubble ${isCloser ? 'bubble-closer' : 'bubble-opponent'}`;
                bubble.innerHTML = `<span class="agent-name">${isCloser ? "Llama-8B (The Closer)" : "Contract Opponent"}</span>`;
                const textContainer = document.createElement('span');
                bubble.appendChild(textContainer);
                duelLog.appendChild(bubble);
                
                await typeText(textContainer, msg.msg);
                await sleep(400);
            }
        }

    } catch (err) {
        alert("CRITICAL SYSTEM FAILURE: Check Console.");
        console.error(err);
    } finally {
        negotiateBtn.disabled = false;
        negotiateBtn.textContent = "Engage Swarm Intelligence";
    }
});
