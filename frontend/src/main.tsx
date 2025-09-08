import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  // StrictMode disabled: causes issues with WebSocket singleton pattern
  // StrictMode double-invokes effects which creates duplicate WebSocket connections
  // ElevenLabs rejects multiple connections, causing immediate disconnection
  <App />,
);
