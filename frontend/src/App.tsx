import { TradingDashboardSimple } from './components/TradingDashboardSimple';
import { ProviderTest } from './components/ProviderTest';
import { IndicatorProvider } from './contexts/IndicatorContext';

function App() {
  // Check URL parameter to show provider test
  const showProviderTest = window.location.search.includes('provider-test');
  
  if (showProviderTest) {
    return <ProviderTest />;
  }
  
  return (
    <IndicatorProvider>
      <TradingDashboardSimple />
    </IndicatorProvider>
  );
}

export default App;
