const scanBtn = document.getElementById('scan-btn');
const targetInput = document.getElementById('target-input');
const resList = document.getElementById('res-list');
const pitchList = document.getElementById('pitch-list');
const radar = document.getElementById('radar');
const dnaBox = document.getElementById('dna-box');
const dnaFill = document.getElementById('dna-fill');
const personalityLabel = document.getElementById('personality-label');
const targetStatus = document.getElementById('target-status');

async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function typeText(element, text, speed = 15) {
    let currentText = "";
    for (let i = 0; i < text.length; i++) {
        currentText += text.charAt(i);
        element.textContent = currentText;
        if (i % 5 === 0) pitchList.scrollTop = pitchList.scrollHeight;
        await sleep(speed);
    }
}

scanBtn.addEventListener('click', async () => {
    const data = targetInput.value.trim();
    if (!data) return alert("NO TARGET DATA PROVIDED.");

    scanBtn.disabled = true;
    scanBtn.textContent = "INFILTRATING TARGET...";
    radar.style.display = 'block';
    targetStatus.textContent = "STATUS: SCANNING DIGITAL FOOTPRINT";
    targetStatus.style.color = "var(--cyan)";
    
    resList.innerHTML = '<div style="text-align: center; color: var(--purple); margin-top: 50px; font-weight: 900; animation: blink 0.5s infinite;">NEURAL RESEARCH IN PROGRESS...</div>';
    pitchList.innerHTML = '';
    dnaBox.style.display = 'none';

    try {
        const res = await fetch('/prospect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_data: data })
        });
        const prospectData = await res.json();
        if (prospectData.error) throw new Error(prospectData.error);

        // 1. Research Points
        resList.innerHTML = '';
        prospectData.research.forEach((point, i) => {
            setTimeout(() => {
                const card = document.createElement('div');
                card.className = 'res-card';
                card.innerHTML = `<div class="res-topic">${point.topic}</div><div class="res-insight">${point.insight}</div>`;
                resList.appendChild(card);
            }, i * 300);
        });

        // 2. Personality DNA
        await sleep(1000);
        dnaBox.style.display = 'block';
        personalityLabel.textContent = `PERSONALITY: ${prospectData.personality.type}`;
        setTimeout(() => {
            dnaFill.style.width = `${prospectData.personality.score}%`;
        }, 100);

        // 3. Pitch Duel
        targetStatus.textContent = "STATUS: GENERATING NEXUS PITCHES";
        for (const pitch of prospectData.pitches) {
            const card = document.createElement('div');
            card.className = 'pitch-card';
            card.innerHTML = `<div class="pitch-subject">${pitch.subject}</div>`;
            const bodySpan = document.createElement('div');
            bodySpan.className = 'pitch-body';
            card.appendChild(bodySpan);
            pitchList.appendChild(card);
            
            await typeText(bodySpan, pitch.body);
            await sleep(1000);
        }

    } catch (err) {
        alert("NEXUS COLLAPSE: Check Console.");
        console.error(err);
    } finally {
        scanBtn.disabled = false;
        scanBtn.textContent = "Initiate Nexus Scan";
        radar.style.display = 'none';
        targetStatus.textContent = "STATUS: SCAN COMPLETE";
    }
});
