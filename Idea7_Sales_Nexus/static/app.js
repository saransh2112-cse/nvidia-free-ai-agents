const msgs = [
    "Scanning LinkedIn public profile...",
    "Deploying Prospect Intelligence Analyst...",
    "Deploying LinkedIn InMail Architect...",
    "Deploying Objection Handler...",
    "Deploying Follow-Up Sequence Writer...",
    "Agents running in parallel — crafting your pitch...",
    "Compiling Nexus Sales Intelligence Report...",
];
let msgInt = null;

async function launchNexus() {
    const slug = document.getElementById("li_slug").value.trim().replace(/^.*linkedin\.com\/in\//,'').replace(/\//,'');
    const your_product = document.getElementById("your_product").value.trim();
    const your_company = document.getElementById("your_company").value.trim();
    const value_prop = document.getElementById("value_prop").value.trim();

    if (!slug || !your_product || !your_company || !value_prop) {
        alert("Please fill in all fields."); return;
    }

    const linkedin_url = `https://www.linkedin.com/in/${slug}`;

    document.getElementById("input-panel").style.display = "none";
    document.getElementById("results").style.display = "none";
    document.getElementById("loading").style.display = "block";

    let i = 0;
    const msgEl = document.getElementById("loading-msg");
    msgEl.textContent = msgs[0];
    msgInt = setInterval(() => { i = (i+1)%msgs.length; msgEl.textContent = msgs[i]; }, 1800);

    try {
        const res = await fetch("/nexus", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ linkedin_url, your_product, your_company, value_prop }),
        });
        const data = await res.json();
        renderResults(data);
    } catch(err) {
        alert("Nexus error: " + err.message);
        resetNexus();
    } finally {
        clearInterval(msgInt);
    }
}

function renderResults(data) {
    document.getElementById("loading").style.display = "none";
    document.getElementById("results").style.display = "block";

    const profile = data.profile || {};
    document.getElementById("p-name").textContent = profile.name || profile.username || "LinkedIn Profile";
    document.getElementById("p-headline").textContent = profile.headline || "Professional · LinkedIn";
    const link = document.getElementById("p-link");
    link.href = profile.url || "#";

    document.getElementById("p-product").textContent = data.your_product || "—";

    const grid = document.getElementById("agents-grid");
    grid.innerHTML = "";
    (data.agents || []).forEach(agent => {
        const card = document.createElement("div");
        card.className = "agent-card";
        card.style.borderColor = agent.color + "30";

        const cleanVerdict = (agent.verdict || "").replace(/\*+/g, "").trim();
        const analysisId = `analysis-${agent.role}`;

        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon" style="background:${agent.color}18;color:${agent.color}">${agent.icon}</div>
                <div class="agent-meta">
                    <div class="role" style="color:${agent.color}">${agent.role}</div>
                    <div class="name">${agent.name}</div>
                </div>
                <button class="copy-btn" onclick="copyText('${analysisId}')">Copy</button>
            </div>
            <div class="agent-body" id="${analysisId}">${fmt(agent.analysis)}</div>
            <div class="agent-verdict" style="background:${agent.color}18;color:${agent.color};border:1px solid ${agent.color}44">
                ${esc(cleanVerdict)}
            </div>
        `;
        grid.appendChild(card);
    });
}

function copyText(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const text = el.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const btn = el.parentElement.querySelector('.copy-btn');
        if (btn) { btn.textContent = "Copied!"; setTimeout(() => btn.textContent = "Copy", 1500); }
    });
}

function fmt(text) {
    if (!text) return "";
    const lines = text.split("\n").filter(Boolean);
    return lines.map((line, i) => {
        let l = esc(line.trim());
        l = l.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#e2e8f0">$1</strong>');
        l = l.replace(/^\*+\s*/,'').replace(/\s*\*+$/,'');
        l = l.replace(/^(•|-|\d+\.)\s+/, '<span style="color:#3b82f6;margin-right:6px">▸</span>');
        if (i === lines.length - 1 && line.includes(":")) {
            l = `<span style="color:#e2e8f0;font-weight:700">${l}</span>`;
        }
        return l;
    }).join("<br>");
}

function esc(s) {
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function resetNexus() {
    document.getElementById("results").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("input-panel").style.display = "block";
}
