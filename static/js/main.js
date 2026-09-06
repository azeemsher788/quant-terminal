// main.js

function initApp() {
    console.log("Initializing Quant Terminal...");

    // 1. Initialize Clock
    const clockEl = document.getElementById('clock');
    if (clockEl) {
        setInterval(() => {
            const now = new Date();
            clockEl.textContent = now.toISOString().split('T')[1].split('.')[0] + ' UTC';
        }, 1000);
    }

    // 2. Initialize TradingView Lightweight Charts
    const chartContainer = document.getElementById('tv-chart');
    let chart = null;
    let candlestickSeries = null;
    
    function createChart() {
        const w = chartContainer.offsetWidth;
        const h = chartContainer.offsetHeight;
        console.log(`Chart container size: ${w}x${h}`);

        if (typeof LightweightCharts === 'undefined') {
            console.error("LightweightCharts library failed to load.");
            chartContainer.innerHTML = '<div style="color:#f44336;padding:1rem;">Charting library not loaded.</div>';
            return;
        }

        try {
            chart = LightweightCharts.createChart(chartContainer, {
                width: w || 600,
                height: h || 400,
                layout: {
                    background: { color: '#1f2833' },
                    textColor: '#c5c6c7',
                },
                grid: {
                    vertLines: { color: 'rgba(102,252,241,0.05)' },
                    horzLines: { color: 'rgba(102,252,241,0.05)' },
                },
                rightPriceScale: { borderColor: 'rgba(102,252,241,0.15)' },
                timeScale: { borderColor: 'rgba(102,252,241,0.15)', timeVisible: true },
            });

            candlestickSeries = chart.addCandlestickSeries({
                upColor: '#4caf50',
                downColor: '#f44336',
                borderUpColor: '#4caf50',
                borderDownColor: '#f44336',
                wickUpColor: '#4caf50',
                wickDownColor: '#f44336',
            });

            window.addEventListener('resize', () => {
                if (chart) chart.applyOptions({
                    width: chartContainer.offsetWidth,
                    height: chartContainer.offsetHeight,
                });
            });

            console.log("Chart initialized successfully.");
        } catch (e) {
            console.error("Chart init error:", e);
        }
    }

    // Wait for browser to finish layout before measuring the container
    setTimeout(createChart, 150);

    // 3. Data Fetching and UI Updating
    const statusBadge = document.getElementById('data-status');
    const priceEl = document.getElementById('current-price');
    const changeEl = document.getElementById('price-change');
    const chartTitle = document.getElementById('chart-title');

    async function loadMarketData(symbol) {
        console.log(`Fetching market data for ${symbol}...`);
        if (statusBadge) {
            statusBadge.textContent = 'FETCHING...';
            statusBadge.className = 'badge';
        }
        
        try {
            const response = await fetch(`/api/market/${symbol}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Failed to fetch data');
            }
            
            const result = await response.json();
            const data = result.data;
            
            if (!data || data.length === 0) throw new Error("No data available");

            if (candlestickSeries && chart) {
                candlestickSeries.setData(data);
                chart.timeScale().fitContent();
            }

            const latest = data[data.length - 1];
            const previous = data[data.length - 2] || latest;
            
            const currentPrice = latest.close;
            const priceChange = currentPrice - previous.close;
            const changePercent = (priceChange / previous.close) * 100;

            if (priceEl && changeEl) {
                priceEl.textContent = `$${currentPrice.toFixed(2)}`;
                const sign = priceChange >= 0 ? '+' : '';
                changeEl.textContent = `${sign}${priceChange.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
                
                priceEl.className = `metric-value ${priceChange >= 0 ? 'up' : 'down'}`;
                changeEl.className = `metric-value ${priceChange >= 0 ? 'up' : 'down'}`;
            }

            if (chartTitle) chartTitle.textContent = `MARKET CHART // ${symbol}`;
            if (statusBadge) {
                statusBadge.textContent = 'CONNECTED';
                statusBadge.className = 'badge success';
            }
            console.log("Market data loaded successfully.");

        } catch (error) {
            console.error('Data loading error:', error);
            if (statusBadge) {
                statusBadge.textContent = 'ERROR';
                statusBadge.className = 'badge error';
            }
            if (priceEl) priceEl.textContent = 'ERROR';
            if (changeEl) changeEl.textContent = '---';
        }
    }

    async function loadNews() {
        console.log("Fetching news...");
        const newsContainer = document.getElementById('news-container');
        if (!newsContainer) return;

        try {
            const response = await fetch('/api/news');
            const data = await response.json();
            
            if (data.error) {
                newsContainer.innerHTML = `<div class="error-msg" style="color:var(--negative);font-size:0.8rem;">${data.error}</div>`;
                return;
            }

            if (!data.news || data.news.length === 0) {
                newsContainer.innerHTML = `<div style="color:var(--text-muted);font-size:0.8rem;">No recent news found.</div>`;
                return;
            }

            const newsHtml = data.news.map(item => `
                <article class="news-item">
                    <span class="news-source">${item.source}</span>
                    <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="news-title">
                        ${item.title}
                    </a>
                    <div class="news-meta">
                        ${formatDate(item.time_published)}
                    </div>
                </article>
            `).join('');
            
            newsContainer.innerHTML = newsHtml;
            console.log("News loaded successfully.");
        } catch (error) {
            console.error('News loading error:', error);
            newsContainer.innerHTML = `<div class="error-msg" style="color:var(--negative);font-size:0.8rem;">Failed to load intelligence feed.</div>`;
        }
    }

    function formatDate(timeString) {
        if (!timeString) return '';
        try {
            const year = timeString.substring(0, 4);
            const month = timeString.substring(4, 6);
            const day = timeString.substring(6, 8);
            return `${year}-${month}-${day}`;
        } catch(e) {
            return timeString;
        }
    }

    // 4. Bind Events
    document.querySelectorAll('.asset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.asset-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const symbol = e.target.dataset.symbol;
            loadMarketData(symbol);
        });
    });

    // 5. Initial Load — delay by 500ms so chart creation (150ms timeout) finishes first
    setTimeout(() => {
        loadMarketData('IBM');
        setTimeout(() => loadNews(), 2000);
    }, 500);
}

// Ensure execution regardless of script load timing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
