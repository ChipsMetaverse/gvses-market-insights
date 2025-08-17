import { VoiceAssistantFixed } from './components/VoiceAssistantFixed';
import { SupabaseProvider } from './hooks/useSupabase';
import './App.css';

function App() {
  return (
    <SupabaseProvider>
      <div className="app">
        <header className="app-header">
          <h1>🎙️ G'sves Market Insights</h1>
          <p>Your Senior Portfolio Manager</p>
        </header>
        <main className="app-main">
          <VoiceAssistantFixed />
        </main>
      </div>
    </SupabaseProvider>
  );
}

export default App;
