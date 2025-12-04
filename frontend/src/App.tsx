import { Routes, Route, Navigate } from 'react-router-dom';
import { TradingDashboardChatOnly } from './components/TradingDashboardChatOnly';
import { TradingDashboardSimple } from './components/TradingDashboardSimple';
import { ProviderTest } from './components/ProviderTest';
import { IndicatorProvider } from './contexts/IndicatorContext';
import { AuthProvider } from './modules/auth/contexts/AuthContext';
import { SignInScreen } from './modules/auth/components/SignInScreen';
import { AuthCallback } from './modules/auth/components/AuthCallback';
import { ProtectedRoute } from './modules/auth/components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/signin" element={<SignInScreen />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <IndicatorProvider>
                <TradingDashboardSimple />
              </IndicatorProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/demo"
          element={
            <IndicatorProvider>
              <TradingDashboardSimple />
            </IndicatorProvider>
          }
        />
        <Route path="/provider-test" element={<ProviderTest />} />
        <Route
          path="/test-chart"
          element={
            <IndicatorProvider>
              <TradingDashboardSimple />
            </IndicatorProvider>
          }
        />
        <Route path="/" element={<Navigate to="/signin" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
