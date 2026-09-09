/**
 * chart.js - Wraps the TradingView Lightweight Charts library.
 */

export class MarketChart {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.chart = null;
        this.candlestickSeries = null;
        
        if (!this.container) {
            console.error(`Container #${containerId} not found.`);
        }
    }

    init() {
        if (typeof LightweightCharts === 'undefined') {
            throw new Error("LightweightCharts library not loaded.");
        }

        const w = this.container.offsetWidth || 600;
        const h = this.container.offsetHeight || 400;

        this.chart = LightweightCharts.createChart(this.container, {
            width: w,
            height: h,
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

        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#4caf50',
            downColor: '#f44336',
            borderUpColor: '#4caf50',
            borderDownColor: '#f44336',
            wickUpColor: '#4caf50',
            wickDownColor: '#f44336',
        });

        window.addEventListener('resize', () => this.handleResize());
    }

    handleResize() {
        if (this.chart && this.container) {
            this.chart.applyOptions({
                width: this.container.offsetWidth,
                height: this.container.offsetHeight,
            });
        }
    }

    setData(data) {
        if (this.candlestickSeries && this.chart) {
            this.candlestickSeries.setData(data);
            this.chart.timeScale().fitContent();
        }
    }

    showError(message) {
        let errorOverlay = this.container.querySelector('.chart-error-overlay');
        if (!errorOverlay) {
            errorOverlay = document.createElement('div');
            errorOverlay.className = 'chart-error-overlay';
            errorOverlay.style.position = 'absolute';
            errorOverlay.style.top = '0';
            errorOverlay.style.left = '0';
            errorOverlay.style.width = '100%';
            errorOverlay.style.height = '100%';
            errorOverlay.style.display = 'flex';
            errorOverlay.style.alignItems = 'center';
            errorOverlay.style.justifyContent = 'center';
            errorOverlay.style.backgroundColor = 'rgba(31, 40, 51, 0.8)';
            errorOverlay.style.color = '#f44336';
            errorOverlay.style.zIndex = '10';
            this.container.style.position = 'relative';
            this.container.appendChild(errorOverlay);
        }
        errorOverlay.textContent = message;
    }

    clearError() {
        const errorOverlay = this.container.querySelector('.chart-error-overlay');
        if (errorOverlay) {
            errorOverlay.remove();
        }
    }
}
