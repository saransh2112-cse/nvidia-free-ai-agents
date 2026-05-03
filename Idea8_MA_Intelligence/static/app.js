const auditBtn = document.getElementById('audit-btn');
const auditInput = document.getElementById('audit-input');
const flagList = document.getElementById('flag-list');
const decisionText = document.getElementById('decision-text');
const justificationText = document.getElementById('justification-text');
const statusText = document.getElementById('status');

// Initialize Radar Chart with "Holographic" styling
const ctx = document.getElementById('riskRadar').getContext('2d');
let riskChart = new Chart(ctx, {
    type: 'radar',
    data: {
        labels: ['FINANCIALS', 'MARKET FIT', 'TEAM', 'LEGAL'],
        datasets: [{
            label: 'Risk Vector',
            data: [20, 20, 20, 20],
            backgroundColor: 'rgba(5, 242, 161, 0.1)',
            borderColor: '#05f2a1',
            pointBackgroundColor: '#05f2a1',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#05f2a1',
            borderWidth: 3
        }]
    },
    options: {
        scales: {
            r: {
                angleLines: { color: 'rgba(5, 242, 161, 0.2)' },
                grid: { color: 'rgba(5, 242, 161, 0.2)' },
                pointLabels: { color: '#05f2a1', font: { size: 12, weight: '900' } },
                suggestedMin: 0,
                suggestedMax: 100,
                ticks: { display: false }
            }
        },
        plugins: { legend: { display: false } },
        responsive: true,
        maintainAspectRatio: false
    }
});

async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function typeText(element, text, speed = 15) {
    element.textContent = "";
    for (let i = 0; i < text.length; i++) {
        element.textContent += text.charAt(i);
        element.scrollTop = element.scrollHeight;
        await sleep(speed);
    }
}

auditBtn.addEventListener('click', async () => {
    const data = auditInput.value.trim();
    if (!data) return alert("TARGET ASSETS NOT DETECTED.");

    auditBtn.disabled = true;
    auditBtn.textContent = "DEPLOYING HUB SWARM...";
    statusText.textContent = "HUB: PROCESSING...";
    
    flagList.innerHTML = '<div style="text-align: center; color: var(--money); margin-top: 50px; font-weight: 900; animation: pulse 1s infinite;">NEURAL AUDIT IN PROGRESS...</div>';
    
    try {
        const res = await fetch('/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_data: data })
        });
        const auditData = await res.json();
        if (auditData.error) throw new Error(auditData.error);

        // 1. Update Radar Chart
        riskChart.data.datasets[0].data = auditData.radar_stats;
        riskChart.update();

        // 2. Update Decision Orb
        decisionText.textContent = auditData.recommendation.decision;
        if (auditData.recommendation.decision === "BUY") {
            decisionText.style.color = "var(--money)";
            decisionText.style.textShadow = "0 0 40px var(--money)";
        } else if (auditData.recommendation.decision === "PASS") {
            decisionText.style.color = "var(--danger)";
            decisionText.style.textShadow = "0 0 40px var(--danger)";
        } else {
            decisionText.style.color = "var(--gold)";
            decisionText.style.textShadow = "0 0 40px var(--gold)";
        }
        
        await typeText(justificationText, auditData.recommendation.justification);

        // 3. Populate Flags
        flagList.innerHTML = '';
        auditData.red_flags.forEach((flag, i) => {
            setTimeout(() => {
                const item = document.createElement('div');
                item.className = 'flag-item';
                item.style.borderLeftColor = flag.severity === "HIGH" ? "var(--danger)" : "var(--gold)";
                item.innerHTML = `<div class="flag-title">${flag.title}</div><div class="flag-body">${flag.impact}</div>`;
                flagList.appendChild(item);
            }, i * 200);
        });

    } catch (err) {
        alert("HUB COLLAPSE: Check Console.");
        console.error(err);
    } finally {
        auditBtn.disabled = false;
        auditBtn.textContent = "Initiate Swarm Audit";
        statusText.textContent = "HUB: AUDIT COMPLETE";
    }
});
