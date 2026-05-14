let activeAgentCard = null;

async function activateSwarm() {
    const brandName = document.getElementById('brandName').value;
    const strategicQuery = document.getElementById('strategicQuery').value;
    const mentions = document.getElementById('mentions').value;
    const feed = document.getElementById('swarmFeed');

    if (!brandName || !mentions) {
        alert("Enter Brand Name and Mentions.");
        return;
    }

    feed.innerHTML = ''; 
    document.getElementById('statusPulseText').innerText = "Initializing Swarm...";
    
    try {
        const response = await fetch('/analyze_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                brand_name: brandName, 
                strategic_query: strategicQuery,
                recent_mentions: mentions 
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.trim().startsWith('data: ')) {
                    try {
                        const payload = JSON.parse(line.replace('data: ', '').trim());
                        if (payload.status) updateStatusPulse(payload.status);
                        if (payload.thought_token) streamThought(payload.agent, payload.thought_token);
                        if (payload.final_data) finalizeAgent(payload.agent, payload.final_data);
                        if (payload.error) markAgentFailed(payload.agent, payload.error);
                    } catch (e) {}
                }
            }
        }

    } catch (error) {
        updateStatusPulse("OFFLINE");
    }
}

function updateStatusPulse(text) {
    document.getElementById('statusPulseText').innerText = text;
}

function markAgentFailed(agentKey, msg) {
    let card = document.getElementById(`agent-${agentKey}`);
    if (!card) {
        card = createAgentCard(agentKey);
        document.getElementById('swarmFeed').appendChild(card);
    }
    const badge = card.querySelector('.active-badge');
    badge.innerText = 'FAILED';
    badge.classList.remove('thinking');
    badge.style.background = 'rgba(255,0,85,0.2)';
    badge.style.color = 'var(--danger)';
    const grid = card.querySelector('.data-grid');
    grid.style.display = 'grid';
    grid.innerHTML = `<div class="data-item"><span class="data-label" style="color:var(--danger)">Error</span><div class="data-content">${msg}</div></div>`;
}

function streamThought(agentKey, token) {
    let card = document.getElementById(`agent-${agentKey}`);
    if (!card) {
        card = createAgentCard(agentKey);
        document.getElementById('swarmFeed').appendChild(card);
    }

    const thoughtBox = card.querySelector('.thought-stream');
    thoughtBox.textContent += token;
    
    const feed = document.getElementById('swarmFeed');
    feed.scrollTop = feed.scrollHeight;
}

function createAgentCard(agentKey) {
    const names = {
        sentiment: 'Behavioral Data Scientist',
        risk: 'Global Risk Strategist',
        content: 'Creative Communications Director',
        audit: 'Chief Orchestrator'
    };

    const card = document.createElement('div');
    card.id = `agent-${agentKey}`;
    card.className = 'agent-report slide-up';
    card.innerHTML = `
        <div class="agent-header">
            <h3>${names[agentKey]}</h3>
            <span class="active-badge thinking">ANALYZING...</span>
        </div>
        <div class="thought-process">
            <span class="thought-label">STRATEGIC REASONING:</span><br>
            <span class="thought-stream"></span>
        </div>
        <div class="data-grid" style="display:none; margin-top: 15px;"></div>
    `;
    return card;
}

function finalizeAgent(agentKey, data) {
    const card = document.getElementById(`agent-${agentKey}`);
    if (!card) return;

    card.querySelector('.active-badge').innerText = 'VERIFIED';
    card.querySelector('.active-badge').classList.remove('thinking');
    
    const grid = card.querySelector('.data-grid');
    grid.style.display = 'grid';

    let metrics = [];
    if (agentKey === 'sentiment') {
        document.getElementById('scoreVal').innerText = (data.score || 0) + '%';
        metrics = [
            { label: 'Market Trajectory', value: data.trajectory },
            { label: 'Risk Profile', value: data.churn_risk },
            { label: 'Key Sentiment Drivers', value: data.key_drivers }
        ];
    } else if (agentKey === 'risk') {
        document.getElementById('crisisVal').innerText = 'Tier ' + (data.crisis_tier || "1");
        metrics = [
            { label: 'Strategic Pillars', value: data.strategic_pillars },
            { label: 'Operational Requirements', value: data.operational_requirements }
        ];
    } else if (agentKey === 'content') {
        metrics = [
            { label: 'Social Response (Twitter)', value: data.tweet || data.twitter_response },
            { label: 'Press Headline', value: data.press_headline || data.formal_statement },
            { label: 'Staff Action', value: data.staff_action || data.internal_memo }
        ];
    } else if (agentKey === 'audit') {
        document.getElementById('auditVal').innerText = 'COMPLETE';
        document.getElementById('auditVal').style.fontSize = '1.2rem';
        metrics = [
            { label: 'Final Verdict', value: data.verdict || data.final_verdict },
            { label: 'Executive Summary', value: data.summary || data.executive_summary },
            { label: 'Critical Adjustments', value: data.actions || data.critical_adjustments },
            { label: 'Swarm Needs to Know', value: data.refining_question, style: 'color: var(--secondary); font-weight: 600;' }
        ];
    }

    grid.innerHTML = metrics.map(m => `
        <div class="data-item" style="${m.style || ''}">
            <span class="data-label">${m.label}</span>
            <div class="data-content">${formatValue(m.value)}</div>
        </div>
    `).join('');
}

function formatValue(val) {
    if (Array.isArray(val)) return `<ul>${val.map(v => `<li>${v}</li>`).join('')}</ul>`;
    if (typeof val === 'object' && val !== null) return JSON.stringify(val, null, 2);
    return val || "N/A";
}
