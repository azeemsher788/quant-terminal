import { fetchMarketData, fetchNews } from './api.js';
import { MarketChart } from './chart.js';
import { UI } from './ui.js';

class App {
    constructor() {
        this.chart = new MarketChart('tv-chart');
    }

    async init() {
        UI.startClock();
        
        try {
            // Delay chart initialization slightly to ensure DOM dimensions are calculated
            setTimeout(() => {
                try {
                    this.chart.init();
                    this.loadMarketData('IBM');
                    this.loadNews();
                } catch (err) {
                    this.chart.showError("Failed to initialize chart components.");
                    console.error(err);
                }
            }, 150);
        } catch (e) {
            console.error("App initialization failed", e);
        }

        UI.bindAssetSelection((symbol) => this.loadMarketData(symbol));
    }

    async loadMarketData(symbol) {
        UI.setStatus('FETCHING...', 'default');
        this.chart.clearError();
        
        try {
            const data = await fetchMarketData(symbol);
            this.chart.setData(data);
            UI.updateMetrics(data, symbol);
            UI.setStatus('CONNECTED', 'success');
        } catch (error) {
            console.error('Data loading error:', error);
            UI.setStatus('ERROR', 'error');
            UI.showErrorMetrics();
            this.chart.showError(error.message || "Failed to load market data");
        }
    }

    async loadNews() {
        try {
            const newsItems = await fetchNews();
            UI.renderNews(newsItems);
        } catch (error) {
            console.error('News loading error:', error);
            UI.showNewsError('Failed to load intelligence feed. Please try again later.');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});
