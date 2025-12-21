import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';
import { initSentry } from './config/sentry';

// Initialize Sentry error tracking as early as possible
initSentry();

ReactDOM.createRoot(document.getElementById('root')!).render(
  // StrictMode disabled: causes issues with WebSocket singleton pattern
  // StrictMode double-invokes effects which creates duplicate WebSocket connections
  // ElevenLabs rejects multiple connections, causing immediate disconnection
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);
