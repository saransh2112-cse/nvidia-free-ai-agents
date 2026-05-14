const msgs = ["Scanning customer signals...","Deploying Churn Signal Analyst...","Deploying Root Cause Detective...","Deploying Retention Architect...","Deploying CS Brief Agent...","Agents running in parallel...","Compiling churn report..."];
let msgInt = null;
async function launchEcho() {
    const company=document.getElementById("company").value.trim();
    const plan=document.getElementById("plan").value.trim();
    const tenure=parseInt(document.getElementById("tenure").value)||12;
    const industry=document.getElementById("industry").value.trim();
    const usage=document.getElementById("usage").value.trim();
    const support=document.getElementById("support").value.trim();
    const billing=document.getElementById("billing").value.trim();
    if(!company||!plan||!industry||!usage||!support||!billing){alert("Please fill in all fields.");return;}
    document.getElementById("input-panel").style.display="none";
    document.getElementById("results").style.display="none";
    document.getElementById("loading").style.display="block";
    let i=0;const msgEl=document.getElementById("loading-msg");
    msgEl.textContent=msgs[0];
    msgInt=setInterval(()=>{i=(i+1)%msgs.length;msgEl.textContent=msgs[i];},1800);
    try {
        const res=await fetch("/echo",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({company,plan,tenure_months:tenure,usage_trend:usage,support_tickets:support,billing_signals:billing,industry})});
        const data=await res.json();
        renderResults(data);
    } catch(err){alert("Echo error: "+err.message);resetEcho();}
    finally{clearInterval(msgInt);}
}
function renderResults(data) {
    document.getElementById("loading").style.display="none";
    document.getElementById("results").style.display="block";
    const score=data.churn_score||50;
    const circ=2*Math.PI*45;
    const fill=document.getElementById("score-fill");
    fill.style.strokeDasharray=circ;
    fill.style.strokeDashoffset=circ-(circ*score/100);
    fill.style.stroke=data.risk_color;
    document.getElementById("score-number").textContent=score;
    document.getElementById("score-number").style.color=data.risk_color;
    document.getElementById("score-company").textContent=data.company;
    document.getElementById("score-plan").textContent=data.plan;
    const badge=document.getElementById("risk-badge");
    badge.textContent="⚠ "+data.risk_level+" CHURN RISK";
    badge.style.background=data.risk_color+"22";
    badge.style.border="1px solid "+data.risk_color+"55";
    badge.style.color=data.risk_color;
    const grid=document.getElementById("agents-grid");
    grid.innerHTML="";
    (data.agents||[]).forEach(agent=>{
        const card=document.createElement("div");
        card.className="agent-card";
        card.style.borderColor=agent.color+"30";
        const cleanVerdict=(agent.verdict||'').replace(/\*+/g,'').trim();
        card.innerHTML=`<div class="agent-header"><div class="agent-icon" style="background:${agent.color}18;color:${agent.color}">${agent.icon}</div><div class="agent-meta"><div class="role" style="color:${agent.color}">${agent.role.replace(/_/g,' ')}</div><div class="name">${agent.name}</div></div></div><div class="agent-body">${fmt(agent.analysis)}</div><div class="agent-verdict" style="background:${agent.color}18;color:${agent.color};border:1px solid ${agent.color}44">${esc(cleanVerdict)}</div>`;
        grid.appendChild(card);
    });
}
function fmt(text){
    if(!text)return"";
    const lines=text.split("\n").filter(Boolean);
    return lines.map((line,i)=>{
        // 1. Escape HTML special chars first
        let l=esc(line.trim());
        // 2. Convert **bold** → <strong> (after esc, * is still *)
        l=l.replace(/\*\*(.+?)\*\*/g,'<strong style="color:#e2e8f0">$1</strong>');
        // 3. Strip any leftover lone asterisks at start/end
        l=l.replace(/^\*+\s*/,'').replace(/\s*\*+$/,'');
        // 4. Convert bullet • or - at line start
        l=l.replace(/^(•|-|\*|\d+\.)\s+/,'<span style="color:#a855f7;margin-right:6px">▸</span>');
        // 5. Bold the verdict line
        if(i===lines.length-1&&line.includes(":")){
            l=`<span style="color:#e2e8f0;font-weight:700">${l}</span>`;
        }
        return l;
    }).join('<br>');
}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function resetEcho(){document.getElementById("results").style.display="none";document.getElementById("loading").style.display="none";document.getElementById("input-panel").style.display="block";}
