const engageBtn = document.getElementById('engage-btn');
const crisisInput = document.getElementById('crisis-input');
const hotspotList = document.getElementById('hotspot-list');
const bloodlineFill = document.getElementById('bloodline-fill');
const statusText = document.getElementById('status-text');

// Strategy Elements
const peaceTitle = document.getElementById('peace-title');
const peaceBody = document.getElementById('peace-body');
const peaceImpact = document.getElementById('peace-impact');

const defTitle = document.getElementById('def-title');
const defBody = document.getElementById('def-body');
const defImpact = document.getElementById('def-impact');

async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function typeText(element, text, speed = 15) {
    element.textContent = "";
    for (let i = 0; i < text.length; i++) {
        element.textContent += text.charAt(i);
        await sleep(speed);
    }
}

engageBtn.addEventListener('click', async () => {
    const text = crisisInput.value.trim();
    if (!text) return alert("NO CRISIS DETECTED. SYSTEM IDLE.");

    engageBtn.disabled = true;
    engageBtn.textContent = "DEPLOYING COUNTER-MEASURES...";
    statusText.textContent = "SIGNAL: EMERGENCY | DEPLOYING SENTINEL SWARM";
    
    hotspotList.innerHTML = '<div style="text-align: center; color: var(--crimson); margin-top: 100px; font-weight: 900; animation: blink 0.5s infinite;">NEURAL INFILTRATION IN PROGRESS...</div>';
    bloodlineFill.style.height = "0%";

    try {
        const res = await fetch('/crisis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ crisis_text: text })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        // 1. Update Bloodline (Outrage Index)
        setTimeout(() => {
            bloodlineFill.style.height = `${data.trust_score}%`;
        }, 500);

        // 2. Update Hotspots
        hotspotList.innerHTML = '';
        data.hotspots.forEach((spot, i) => {
            setTimeout(() => {
                const item = document.createElement('div');
                item.className = 'hotspot-item';
                item.innerHTML = `<div class="hotspot-area">${spot.area} [${spot.severity}]</div><div class="hotspot-desc">${spot.sentiment}</div>`;
                hotspotList.appendChild(item);
            }, i * 300);
        });

        // 3. Narrative Duel
        statusText.textContent = "SIGNAL: DUELING NARRATIVES | CALCULATING IMPACT";
        
        // Peacekeeper
        peaceTitle.textContent = data.strategies.peacekeeper.title;
        peaceImpact.textContent = `EST. RECOVERY: ${data.strategies.peacekeeper.impact}`;
        await typeText(peaceBody, data.strategies.peacekeeper.body);

        // Defender
        defTitle.textContent = data.strategies.defender.title;
        defImpact.textContent = `EST. RECOVERY: ${data.strategies.defender.impact}`;
        await typeText(defBody, data.strategies.defender.body);

    } catch (err) {
        alert("SENTINEL COLLAPSE: Check Console.");
        console.error(err);
    } finally {
        engageBtn.disabled = false;
        engageBtn.textContent = "Deploy Sentinel Swarm";
        statusText.textContent = "SIGNAL: RESPONSE READY | SELECT NARRATIVE";
    }
});
