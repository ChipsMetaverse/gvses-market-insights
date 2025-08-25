import { createChart } from 'lightweight-charts';

const container = document.createElement('div');
const chart = createChart(container, { width: 400, height: 300 });
console.log('Chart methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(chart)));
console.log('Has addLineSeries:', typeof chart.addLineSeries);
