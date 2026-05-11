const loadingMessages = [
    "Scanning live global disruption feeds...",
    "Deploying Geo-Political Intelligence Officer...",
    "Deploying Route Risk Analyst...",
    "Deploying Re-Route Strategist...",
    "Deploying Carrier Contract Agent...",
    "Agents running in parallel — synthesizing intelligence...",
    "Compiling Atlas Disruption Report...",
];

let msgInterval = null;

async function launchAtlas() {
    const origin = document.getElementById("origin").value.trim();
    const destination = document.getElementById("destination").value.trim();
    const cargo = document.getElementById("cargo").value.trim();
    const carrier = document.getElementById("carrier").value.trim();

    if (!origin || !destination || !cargo || !carrier) {
        alert("Please fill in all shipment fields.");
        return;
    }

    // Show loading
    document.getElementById("input-panel").style.display = "none";
    document.getElementById("results").style.display = "none";
    document.getElementById("loading").style.display = "block";

    // Cycle loading messages
    let i = 0;
    const msgEl = document.getElementById("loading-msg");
    msgEl.textContent = loadingMessages[0];
    msgInterval = setInterval(() => {
        i = (i + 1) % loadingMessages.length;
        msgEl.textContent = loadingMessages[i];
    }, 1800);

    try {
        const res = await fetch("/atlas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ origin, destination, cargo, carrier }),
        });
        const data = await res.json();
        renderResults(data);
    } catch (err) {
        alert("Atlas swarm error: " + err.message);
        resetAtlas();
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

    // Route summary
    document.getElementById("sum-origin").textContent = data.origin;
    document.getElementById("sum-destination").textContent = data.destination;
    document.getElementById("sum-cargo").textContent = data.cargo;

    const badge = document.getElementById("risk-badge");
    badge.textContent = `⚠ ${data.overall_risk} RISK`;
    badge.style.background = data.risk_color + "22";
    badge.style.border = `1px solid ${data.risk_color}55`;
    badge.style.color = data.risk_color;

    // Agent cards
    const grid = document.getElementById("agents-grid");
    grid.innerHTML = "";
    (data.agents || []).forEach(agent => {
        const card = document.createElement("div");
        card.className = "agent-card";
        card.style.borderColor = agent.color + "30";
        card.style.boxShadow = `inset 0 0 30px ${agent.color}08`;

        // Determine status badge colors
        const statusText = (agent.status || "").toUpperCase();
        let statusBg = agent.color + "22";
        let statusColor = agent.color;

        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon" style="background:${agent.color}18; color:${agent.color}">
                    ${agent.icon}
                </div>
                <div class="agent-meta">
                    <div class="role" style="color:${agent.color}">${agent.role}</div>
                    <div class="name">${agent.name}</div>
                </div>
            </div>
            <div class="agent-body">${formatAnalysis(agent.analysis)}</div>
            <div class="agent-status" style="background:${statusBg}; color:${statusColor}; border:1px solid ${statusColor}44">
                ${statusText}
            </div>
        `;
        grid.appendChild(card);
    });

    // Verdict
    const verdict = document.getElementById("verdict");
    const decision = document.getElementById("verdict-decision");

    let verdictText, verdictSub, bgColor, borderColor;
    switch (data.overall_risk) {
        case "CRITICAL":
            verdictText = "🚨 IMMEDIATE REROUTE";
            verdictSub = "Critical threat detected — autonomous re-routing brief drafted.";
            bgColor = "rgba(239,68,68,0.08)";
            borderColor = "rgba(239,68,68,0.3)";
            break;
        case "HIGH":
            verdictText = "⚠️ REROUTE RECOMMENDED";
            verdictSub = "High risk on primary route — alternative carriers and lanes identified.";
            bgColor = "rgba(249,115,22,0.08)";
            borderColor = "rgba(249,115,22,0.3)";
            break;
        case "MODERATE":
            verdictText = "🟡 MONITOR & STANDBY";
            verdictSub = "Moderate risk — proceed with contingency plans on standby.";
            bgColor = "rgba(234,179,8,0.08)";
            borderColor = "rgba(234,179,8,0.3)";
            break;
        default:
            verdictText = "✅ PROCEED — ROUTE CLEAR";
            verdictSub = "No critical disruptions detected. Primary route viable.";
            bgColor = "rgba(34,197,94,0.08)";
            borderColor = "rgba(34,197,94,0.3)";
    }

    verdict.style.background = bgColor;
    verdict.style.borderColor = borderColor;
    decision.textContent = verdictText;
    document.getElementById("verdict-sub").textContent = verdictSub;
}

function formatAnalysis(text) {
    if (!text) return "";
    // Bold the last line (status)
    const lines = text.split("\n").filter(Boolean);
    return lines.map((line, i) => {
        if (i === lines.length - 1 && line.includes(":")) {
            return `<strong style="color:#e2e8f0">${escapeHtml(line)}</strong>`;
        }
        return escapeHtml(line);
    }).join("<br>");
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function resetAtlas() {
    document.getElementById("results").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("input-panel").style.display = "block";
}
