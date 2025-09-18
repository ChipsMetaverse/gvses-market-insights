// Test to see what methods are available on createChart
import { createChart } from 'lightweight-charts';

const container = document.createElement('div');
const chart = createChart(container);

console.log('Chart methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(chart)));

// Check if there are any series creation methods
const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(chart));
const seriesMethods = methods.filter(m => m.includes('Series') || m.includes('add'));
console.log('Series creation methods:', seriesMethods);