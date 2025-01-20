const ctx = document.getElementById('priceChart').getContext('2d');

async function fetchMoexData(ticker) {
    const url = `https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/${ticker}/candles.json?interval=24&from=2024-01-01`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.candles && data.candles.data.length > 0) {
            const candles = data.candles.data;
            const prices = candles.map(item => item[4]); // Цена закрытия

            return { prices };
        } else {
            console.error('Ошибка получения данных для тикера:', ticker);
            return null;
        }
    } catch (error) {
        console.error('Ошибка при запросе MOEX API:', error);
        return null;
    }
}


async function renderCharts() {
    const tickers = [
        { name: 'Сбербанк', symbol: 'SBER' },
        { name: 'Лукойл', symbol: 'LKOH' },
        { name: 'Яндекс', symbol: 'YNDX' },
        { name: 'Роснефть', symbol: 'ROSN' },
        { name: 'ВТБ', symbol: 'VTBR' },
        { name: 'Татнефть', symbol: 'TATN' },
        { name: 'Газпром', symbol: 'GAZP' }
    ];

    const datasets = [];
    let labels = [];

    for (const stock of tickers) {
        const data = await fetchMoexData(stock.symbol);
        if (data) {
            if (labels.length === 0) labels = data.dates; 
            datasets.push({
                label: `${stock.name} (${stock.symbol})`,
                data: data.prices,
                borderColor: getRandomColor(),
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.4
            });
        }
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true, position: 'top', labels: { color: '#ffffff' } }
            },
            scales: {
                x: { ticks: { color: '#ffffff' } },
                y: { ticks: { color: '#ffffff' } }
            }
        }
    });
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

renderCharts();

async function updateStockList() {
    const tickers = [
        { name: 'Сбербанк', symbol: 'SBER' },
        { name: 'Лукойл', symbol: 'LKOH' },
        { name: 'Яндекс', symbol: 'YNDX' },
        { name: 'Роснефть', symbol: 'ROSN' },
        { name: 'ВТБ', symbol: 'VTBR' },
        { name: 'Татнефть', symbol: 'TATN' },
        { name: 'Газпром', symbol: 'GAZP' }
    ];

    const stockList = document.getElementById('stock-list');
    stockList.innerHTML = ''; 

    for (const stock of tickers) {
        try {
            const price = await fetchMoexPrice(stock.symbol);
            if (price !== null) {
                const stockItem = document.createElement('div');
                stockItem.className = 'stock-item';
                stockItem.innerHTML = `
                    <span>${stock.name}</span>
                    <span class="price">${price.toFixed(2)} ₽</span>
                `;

                stockList.appendChild(stockItem);
            } else {
                console.error(`Не удалось получить цену для ${stock.name}`);
            }
        } catch (error) {
            console.error(`Ошибка загрузки данных для ${stock.name}: ${error}`);
        }
    }
}

async function fetchMoexPrice(ticker) {
    const url = `https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/${ticker}.json`;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Ошибка загрузки данных с MOEX API');
        const data = await response.json();

        const marketData = data['marketdata']['data'];
        if (marketData.length > 0) {
            return parseFloat(marketData[0][12]); // Цена последней сделки
        }
        return null;
    } catch (error) {
        console.error(`Ошибка при запросе MOEX API для тикера ${ticker}: ${error}`);
        return null;
    }
}

async function fetchHistoricalStockData(ticker) {
    const today = new Date().toISOString().split('T')[0]; // Текущая дата в формате YYYY-MM-DD
    const response = await fetch(`https://api.example.com/stocks/${ticker}/history?start=2014-06-09&end=${today}`);
    const data = await response.json();

    return data; 
}

async function displayCurrentStockData(ticker) {
    const response = await fetch(`https://api.example.com/stocks/${ticker}/current`);
    const data = await response.json();

    document.getElementById('stock-price').textContent = data.currentPrice;
    document.getElementById('change-24h').textContent = data.change24h;
    document.getElementById('max-24h').textContent = data.max24h;
    document.getElementById('min-24h').textContent = data.min24h;
    document.getElementById('volume-24h-stocks').textContent = data.volume24hStocks;
    document.getElementById('volume-24h-rub').textContent = data.volume24hRub;
    document.getElementById('prev-close-price').textContent = data.prevClosePrice;
    document.getElementById('min-price').textContent = data.minPrice;
    document.getElementById('trade-volume').textContent = data.tradeVolume;
    document.getElementById('trade-volume-qty').textContent = data.tradeVolumeQty;
    document.getElementById('last-trade-price').textContent = data.lastTradePrice;
    document.getElementById('market-price-2').textContent = data.marketPrice2;
    document.getElementById('market-price-z').textContent = data.marketPriceZ;
    document.getElementById('open-price').textContent = data.openPrice;
    document.getElementById('max-price').textContent = data.maxPrice;
    document.getElementById('first-trade-volume').textContent = data.firstTradeVolume;
    document.getElementById('last-trade-volume').textContent = data.lastTradeVolume;
    document.getElementById('trades-market-2').textContent = data.tradesMarket2;
    document.getElementById('trades-market-3').textContent = data.tradesMarket3;
}

async function renderStockChart(ticker) {
    const historicalData = await fetchHistoricalStockData(ticker);
    
    const labels = historicalData.map(item => item.date); // Даты
    const prices = historicalData.map(item => item.close); // Цены закрытия

    const ctx = document.getElementById('stock-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Цена акций',
                data: prices,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'month',
                        tooltipFormat: 'MMM DD, YYYY'
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    displayCurrentStockData('SBER'); 
    renderStockChart('SBER');
});



updateStockList();
setInterval(updateStockList, 30000);    