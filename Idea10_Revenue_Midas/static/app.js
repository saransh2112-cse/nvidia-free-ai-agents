const midasBtn = document.getElementById('midas-btn');
const marketInput = document.getElementById('market-input');
const arbList = document.getElementById('arb-list');
const offerList = document.getElementById('offer-list');
const profitVal = document.getElementById('profit-val');
const pulseRing = document.getElementById('pulse-ring');

async function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

midasBtn.addEventListener('click', async () => {
    const data = marketInput.value.trim();
    if (!data) return alert("NO MARKET ASSETS DETECTED.");

    midasBtn.disabled = true;
    midasBtn.textContent = "TRANSMUTING DATA TO GOLD...";
    
    arbList.innerHTML = '<div style="text-align: center; color: var(--gold); margin-top: 50px; font-weight: 900; animation: pulse 1s infinite;">NEURAL ARBITRAGE IN PROGRESS...</div>';
    offerList.innerHTML = '';
    profitVal.textContent = "00";
    pulseRing.style.animation = "none";

    try {
        const res = await fetch('/revenue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ market_data: data })
        });
        const midasData = await res.json();
        if (midasData.error) throw new Error(midasData.error);

        // 1. Profit Lift Animation
        let current = 0;
        const interval = setInterval(() => {
            if (current >= midasData.forecast) {
                clearInterval(interval);
                profitVal.textContent = midasData.forecast + "%";
                pulseRing.style.animation = "pulse 2s infinite";
            } else {
                current += 1;
                profitVal.textContent = current < 10 ? `0${current}%` : `${current}%`;
            }
        }, 40);

        // 2. Arbitrage Cards
        arbList.innerHTML = '';
        midasData.arbitrage.forEach((arb, i) => {
            setTimeout(() => {
                const card = document.createElement('div');
                card.className = 'arb-card';
                card.innerHTML = `
                    <div class="arb-product">${arb.product}</div>
                    <div class="arb-action">${arb.action}</div>
                    <div class="arb-reason">${arb.reason}</div>
                `;
                arbList.appendChild(card);
            }, i * 300);
        });

        // 3. Flash Offers
        midasData.flash_offers.forEach((offer, i) => {
            setTimeout(() => {
                const card = document.createElement('div');
                card.className = 'offer-card';
                card.innerHTML = `
                    <div class="offer-headline">${offer.headline}</div>
                    <div class="offer-desc">${offer.description}</div>
                `;
                offerList.appendChild(card);
            }, i * 600);
        });

    } catch (err) {
        alert("MIDAS COLLAPSE: Check Console.");
        console.error(err);
    } finally {
        midasBtn.disabled = false;
        midasBtn.textContent = "Execute Revenue Pivot";
    }
});
