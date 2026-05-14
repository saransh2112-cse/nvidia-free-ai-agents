const msgs=["Benchmarking against market data...","Deploying Salary Benchmarker...","Deploying Flight Risk Profiler...","Deploying Retention Package Architect...","Deploying HR Brief Agent...","Agents running in parallel...","Compiling talent retention report..."];
let msgInt=null;
async function launchVertex(){
    const name=document.getElementById("emp_name").value.trim();
    const role=document.getElementById("role").value.trim();
    const dept=document.getElementById("dept").value.trim();
    const location=document.getElementById("location").value.trim();
    const tenure=parseFloat(document.getElementById("tenure").value)||1;
    const salary=parseInt(document.getElementById("salary").value)||100000;
    const raise=parseInt(document.getElementById("raise").value)||12;
    const perf=document.getElementById("perf").value.trim();
    const signals=document.getElementById("signals").value.trim();
    if(!name||!role||!dept||!location||!signals){alert("Please fill in all fields.");return;}
    document.getElementById("input-panel").style.display="none";
    document.getElementById("results").style.display="none";
    document.getElementById("loading").style.display="block";
    let i=0;const msgEl=document.getElementById("loading-msg");
    msgEl.textContent=msgs[0];
    msgInt=setInterval(()=>{i=(i+1)%msgs.length;msgEl.textContent=msgs[i];},1800);
    try{
        const res=await fetch("/vertex",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,role,department:dept,tenure_years:tenure,current_salary:salary,location,recent_signals:signals,performance:perf,last_raise_months:raise})});
        const data=await res.json();
        renderResults(data);
    }catch(err){alert("Vertex error: "+err.message);resetVertex();}
    finally{clearInterval(msgInt);}
}
function renderResults(data){
    document.getElementById("loading").style.display="none";
    document.getElementById("results").style.display="block";
    const score=data.flight_score||50;
    const circ=2*Math.PI*45;
    const fill=document.getElementById("score-fill");
    fill.style.strokeDasharray=circ;
    fill.style.strokeDashoffset=circ-(circ*score/100);
    fill.style.stroke=data.risk_color;
    document.getElementById("score-number").textContent=score;
    document.getElementById("score-number").style.color=data.risk_color;
    document.getElementById("score-name").textContent=data.name;
    document.getElementById("score-role").textContent=data.role+" · "+data.department;
    const badge=document.getElementById("risk-badge");
    badge.textContent="🎯 "+data.risk_level+" FLIGHT RISK";
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
        let l=esc(line.trim());
        l=l.replace(/\*\*(.+?)\*\*/g,'<strong style="color:#e2e8f0">$1</strong>');
        l=l.replace(/^\*+\s*/,'').replace(/\s*\*+$/,'');
        l=l.replace(/^(•|-|\*|\d+\.)\s+/,'<span style="color:#22c55e;margin-right:6px">▸</span>');
        if(i===lines.length-1&&line.includes(":")){
            l=`<span style="color:#e2e8f0;font-weight:700">${l}</span>`;
        }
        return l;
    }).join('<br>');
}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function resetVertex(){document.getElementById("results").style.display="none";document.getElementById("loading").style.display="none";document.getElementById("input-panel").style.display="block";}
