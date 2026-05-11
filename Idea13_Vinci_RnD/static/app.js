const loadingMessages = [
    "Scanning live market intelligence feeds...",
    "Deploying Patent Intelligence Scout...",
    "Deploying Competitor Market Analyst...",
    "Deploying Innovation Gap Detector...",
    "Deploying Product Design Architect...",
    "Agents running in parallel — synthesizing findings...",
    "Compiling Vinci Product Intelligence Report...",
];

let msgInterval = null;

async function launchVinci() {
    const product_idea = document.getElementById("product_idea").value.trim();
    const market = document.getElementById("market").value.trim();
    const target_user = document.getElementById("target_user").value.trim();

    if (!product_idea || !market || !target_user) {
        alert("Please fill in all research fields.");
        return;
    }

    document.getElementById("input-panel").style.display = "none";
    document.getElementById("results").style.display = "none";
    document.getElementById("loading").style.display = "block";

    let i = 0;
    const msgEl = document.getElementById("loading-msg");
    msgEl.textContent = loadingMessages[0];
    msgInterval = setInterval(() => {
        i = (i + 1) % loadingMessages.length;
        msgEl.textContent = loadingMessages[i];
    }, 1800);

    try {
        const res = await fetch("/vinci", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_idea, market, target_user }),
        });
        const data = await res.json();
        renderResults(data);
    } catch (err) {
        alert("Vinci swarm error: " + err.message);
        resetVinci();
    } finally {
        clearInterval(msgInterval);
    }
}

function renderResults(data) {
    document.getElementById("loading").style.display = "none";
    document.getElementById("results").style.display = "block";

    // Headlines
    const hList = document.getElementById("headlines-list");
    hList.innerHTML = "";
    (data.headlines || []).forEach(h => {
        const li = document.createElement("li");
        li.textContent = h;
        hList.appendChild(li);
    });

    // Idea summary
    document.getElementById("sum-idea").textContent = data.product_idea;
    document.getElementById("sum-market").textContent = data.market;
    document.getElementById("sum-user").textContent = data.target_user;

    const badge = document.getElementById("rec-badge");
    badge.textContent = `🎯 ${data.recommendation}`;
    badge.style.background = data.rec_color + "22";
    badge.style.border = `1px solid ${data.rec_color}55`;
    badge.style.color = data.rec_color;

    // Agent cards
    const grid = document.getElementById("agents-grid");
    grid.innerHTML = "";
    (data.agents || []).forEach(agent => {
        const card = document.createElement("div");
        card.className = "agent-card";
        card.style.borderColor = agent.color + "30";
        card.style.boxShadow = `inset 0 0 30px ${agent.color}08`;

        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon" style="background:${agent.color}18; color:${agent.color}">
                    ${agent.icon}
                </div>
                <div class="agent-meta">
                    <div class="role" style="color:${agent.color}">${agent.role.replace(/_/g, ' ')}</div>
                    <div class="name">${agent.name}</div>
                </div>
            </div>
            <div class="agent-body">${formatText(agent.analysis)}</div>
            <div class="agent-verdict"
                 style="background:${agent.color}18; color:${agent.color}; border:1px solid ${agent.color}44">
                ${escapeHtml(agent.verdict || '')}
            </div>
        `;
        grid.appendChild(card);
    });

    // Recommendation
    const rec = document.getElementById("recommendation");
    const recDec = document.getElementById("rec-decision");
    let emoji, sub, bg, border;

    switch (data.recommendation) {
        case "LAUNCH NOW":
            emoji = "🚀 LAUNCH NOW";
            sub = "Strong IP position, clear market gap, and high feasibility — move to MVP.";
            bg = "rgba(34,197,94,0.08)"; border = "rgba(34,197,94,0.3)";
            break;
        case "VALIDATE FIRST":
            emoji = "🔬 VALIDATE FIRST";
            sub = "Promising opportunity detected — run a lean prototype to de-risk before full build.";
            bg = "rgba(245,158,11,0.08)"; border = "rgba(245,158,11,0.3)";
            break;
        default:
            emoji = "🔄 PIVOT REQUIRED";
            sub = "IP risks and market saturation detected — reconsider core differentiation.";
            bg = "rgba(239,68,68,0.08)"; border = "rgba(239,68,68,0.3)";
    }

    rec.style.background = bg;
    rec.style.borderColor = border;
    recDec.textContent = emoji;
}

function formatText(text) {
    if (!text) return "";
    const lines = text.split("\n").filter(Boolean);
    return lines.map((line, i) => {
        if (i === lines.length - 1 && line.includes(":")) {
            return `<strong style="color:#e2e8f0">${escapeHtml(line)}</strong>`;
        }
        return escapeHtml(line);
    }).join("<br>");
}

function escapeHtml(str) {
    return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function resetVinci() {
    document.getElementById("results").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("input-panel").style.display = "block";
}
