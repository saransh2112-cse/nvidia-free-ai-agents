const conveneBtn = document.getElementById('convene-btn');
const companyInput = document.getElementById('company-input');
const tickerInput = document.getElementById('ticker-input');
const decisionInput = document.getElementById('decision-input');
const boardroom = document.getElementById('boardroom');
const boardDecision = document.getElementById('board-decision');
const newsStrip = document.getElementById('news-strip');
const statusText = document.getElementById('status-text');

// Pre-fill skeleton exec cards
const EXECS = [
    { role: 'CFO', icon: '💰', color: '#22c55e' },
    { role: 'COO', icon: '⚙️', color: '#3b82f6' },
    { role: 'CTO', icon: '💻', color: '#a855f7' },
    { role: 'CMO', icon: '📣', color: '#f97316' },
    { role: 'LEGAL', icon: '⚖️', color: '#ef4444' },
];

function buildSkeletonCards() {
    boardroom.innerHTML = '';
    EXECS.forEach(exec => {
        const card = document.createElement('div');
        card.className = 'exec-card';
        card.id = `card-${exec.role}`;
        card.style.setProperty('--exec-color', exec.color);
        card.innerHTML = `
            <div class="exec-icon">${exec.icon}</div>
            <div class="exec-role">${exec.role}</div>
            <div class="exec-title">Awaiting session...</div>
            <div class="exec-analysis" id="analysis-${exec.role}" style="color:#2d3748;">
                ███ ██████ ████████ ███ ████
                ██████ ███ ██████ ████
                ███████ ████ ██████
            </div>
        `;
        boardroom.appendChild(card);
    });
}
buildSkeletonCards();

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function typeText(el, text, speed = 10) {
    el.textContent = '';
    for (let char of text) {
        el.textContent += char;
        await sleep(speed);
    }
}

conveneBtn.addEventListener('click', async () => {
    const company = companyInput.value.trim();
    const ticker = tickerInput.value.trim().toUpperCase();
    const decision = decisionInput.value.trim();
    if (!company || !ticker || !decision) {
        alert('Please fill in all fields before convening the board.');
        return;
    }

    conveneBtn.disabled = true;
    conveneBtn.textContent = 'CONVENING...';
    boardDecision.style.display = 'none';
    newsStrip.style.display = 'none';
    statusText.textContent = 'NEURAL AGENTS DEPLOYING — FETCHING LIVE MARKET DATA...';

    // Reset cards
    buildSkeletonCards();
    document.getElementById('intel-price').textContent = '...';
    document.getElementById('intel-exchange').textContent = '...';
    document.getElementById('intel-verdict').textContent = '...';
    document.getElementById('intel-consensus').textContent = '...';

    try {
        statusText.textContent = 'RUNNING 5 PARALLEL AGENTS + LIVE MARKET FEED...';

        const res = await fetch('/boardroom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company, ticker, decision })
        });
        const data = await res.json();

        // ── Market Intel Strip ──
        const price = data.market_data?.price ?? 'N/A';
        const prev = data.market_data?.prev_close ?? 0;
        const change = price !== 'N/A' ? ((price - prev) / prev * 100).toFixed(2) : 0;
        const priceEl = document.getElementById('intel-price');
        const changeEl = document.getElementById('intel-change');
        priceEl.textContent = `$${price}`;
        changeEl.textContent = `${change >= 0 ? '▲' : '▼'} ${Math.abs(change)}% today`;
        changeEl.className = `intel-sub ${change >= 0 ? 'positive' : 'negative'}`;
        document.getElementById('intel-exchange').textContent = data.market_data?.exchange ?? 'N/A';
        document.getElementById('intel-verdict').textContent = data.board_decision;
        document.getElementById('intel-consensus').textContent =
            `${data.tally.approve}A · ${data.tally.conditional}C · ${data.tally.reject}R`;

        // ── News Strip ──
        if (data.news?.length) {
            const newsItems = document.getElementById('news-items');
            newsItems.innerHTML = data.news.map(n => `<span class="news-item">${n}</span>`).join('');
            newsStrip.style.display = 'flex';
        }

        // ── Exec Cards with staggered reveal ──
        statusText.textContent = 'BOARD IN SESSION — INTELLIGENCE BRIEFING IN PROGRESS...';
        for (let i = 0; i < data.executives.length; i++) {
            const exec = data.executives[i];
            const card = document.getElementById(`card-${exec.role}`);
            if (!card) continue;
            card.style.setProperty('--exec-color', exec.color);
            card.innerHTML = `
                <div class="exec-icon">${exec.icon}</div>
                <div class="exec-role">${exec.role}</div>
                <div class="exec-title">${exec.name}</div>
                <div class="exec-analysis" id="analysis-${exec.role}"></div>
                <div class="exec-verdict verdict-${exec.verdict}">${exec.verdict}</div>
            `;
            card.classList.add('active');
            await typeText(document.getElementById(`analysis-${exec.role}`), exec.analysis, 8);
            await sleep(200);
        }

        // ── Board Decision ──
        const decisionResult = document.getElementById('decision-result');
        decisionResult.textContent = data.board_decision;
        decisionResult.style.color = data.board_color;
        boardDecision.style.setProperty('--decision-color', data.board_color);
        boardDecision.style.setProperty('--decision-color-transparent', `${data.board_color}15`);
        document.getElementById('tally-approve').textContent = data.tally.approve;
        document.getElementById('tally-conditional').textContent = data.tally.conditional;
        document.getElementById('tally-reject').textContent = data.tally.reject;
        boardDecision.style.display = 'block';

        statusText.textContent = `BOARD SESSION COMPLETE — ${data.board_decision} | ${company} | ${ticker}`;

    } catch (err) {
        statusText.textContent = 'BOARD SESSION ERROR — Check Console';
        console.error(err);
    } finally {
        conveneBtn.disabled = false;
        conveneBtn.textContent = 'Convene Board';
    }
});
