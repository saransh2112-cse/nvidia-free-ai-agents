// Ultimate Resilience Edition
function startEngine() {
    const feed = document.getElementById('activity-feed');
    const addFeed = (msg, isError = false) => {
        const item = document.createElement('div');
        item.className = `feed-item ${isError ? 'error' : ''}`;
        item.innerHTML = `<span>[${new Date().toLocaleTimeString([], { hour12: false })}]</span> ${msg}`;
        feed.appendChild(item);
        feed.scrollTop = feed.scrollHeight;
    };

    // Aggressive library detection
    const Lib = window.ForceGraph3D || window['3d-force-graph'] || window.ForceGraph;
    if (!window.THREE || !Lib) {
        addFeed("Syncing Visual Core...", true);
        setTimeout(startEngine, 1000);
        return;
    }

    addFeed("Visual Engine: ONLINE. ✅");
    const T = window.THREE;

    const Graph = Lib()(document.getElementById('3d-graph'))
        .nodeAutoColorBy('group')
        .linkOpacity(0.4)
        .linkColor(() => '#ffffff')
        .linkWidth(0.5)
        .linkDirectionalParticles(2)
        .linkDirectionalParticleSpeed(0.005)
        .d3AlphaDecay(0.02)
        .backgroundColor('#020617')
        .nodeThreeObject(node => {
            const group = new T.Group();
            // Glowing Sphere
            group.add(new T.Mesh(
                new T.SphereGeometry(node.val / 2 || 5),
                new T.MeshPhongMaterial({ color: node.color || '#3b82f6', transparent: true, opacity: 0.9, emissive: node.color || '#3b82f6', emissiveIntensity: 0.5 })
            ));
            // Label
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            const text = node.name;
            context.font = 'Bold 28px Outfit';
            const textWidth = context.measureText(text).width;
            canvas.width = textWidth + 40; canvas.height = 60;
            context.fillStyle = 'rgba(15, 23, 42, 0.8)'; context.fillRect(0, 5, canvas.width, 50);
            context.strokeStyle = node.color || '#3b82f6'; context.lineWidth = 2; context.strokeRect(0, 5, canvas.width, 50);
            context.fillStyle = '#ffffff'; context.textAlign = 'center'; context.fillText(text, canvas.width / 2, 40);
            const sprite = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(canvas), depthTest: false }));
            sprite.scale.set(canvas.width / 12, 5, 1); sprite.position.y = (node.val / 2 || 5) + 10;
            group.add(sprite);
            return group;
        })
        .onNodeClick(node => {
            const distance = 150;
            const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
            Graph.cameraPosition({ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, node, 1500);
            document.getElementById('details-panel').style.display = 'block';
            document.getElementById('detail-title').textContent = node.name;
            document.getElementById('detail-desc').textContent = node.desc;
            document.getElementById('detail-title').style.color = node.color;
        });

    const btn = document.getElementById('launch-btn');
    btn.addEventListener('click', async () => {
        const topic = document.getElementById('topic-input').value.trim();
        if (!topic) return;
        btn.disabled = true;
        btn.textContent = "Swarm Active...";
        addFeed(`Launching Swarm: ${topic}`);
        try {
            const res = await fetch('/generate_graph', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic }) });
            const data = await res.json();
            Graph.graphData(data);
            setTimeout(() => addFeed("Knowledge Canvas Online. ✅"), 1000);
        } catch (err) { addFeed("Sync failed.", true); }
        finally {
            btn.disabled = false;
            btn.textContent = "Deploy Swarm";
        }
    });
}

// Ensure execution
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startEngine);
} else {
    startEngine();
}
