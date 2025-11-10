import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load environment variables based on mode
  const env = loadEnv(mode, process.cwd(), '');
  
  // Force production API URL for production builds
  if (mode === 'production' || command === 'build') {
    env.VITE_API_URL = 'https://gvses-market-insights.fly.dev';
    env.VITE_WS_URL = 'wss://gvses-market-insights.fly.dev';
  }
  
  const config = {
    plugins: [react()],
    define: {
      // Explicitly define environment variables for build-time substitution
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || (mode === 'production' ? 'https://gvses-market-insights.fly.dev' : 'http://localhost:8000')),
      'import.meta.env.VITE_WS_URL': JSON.stringify(env.VITE_WS_URL || (mode === 'production' ? 'wss://gvses-market-insights.fly.dev' : 'ws://localhost:8000')),
      'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(env.VITE_SUPABASE_URL),
      'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(env.VITE_SUPABASE_ANON_KEY),
      'import.meta.env.VITE_ELEVENLABS_AGENT_ID': JSON.stringify(env.VITE_ELEVENLABS_AGENT_ID),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    esbuild: {
      target: 'esnext',
      logOverride: { 'this-is-undefined-in-esm': 'silent' }
    },
    build: {
      target: 'esnext',
      minify: false, // DISABLE MINIFICATION TO PRESERVE CONSOLE.LOG
      sourcemap: false,
      rollupOptions: {
        onwarn(warning, warn) {
          // Skip certain warnings
          if (warning.code === 'MODULE_LEVEL_DIRECTIVE') return
          warn(warning)
        }
      }
    }
  };

  // Only add server configuration in development mode
  if (command === 'serve') {
    config.server = {
      port: 5174,
      host: true,
      allowedHosts: [
        'localhost',
        '127.0.0.1',
        'host.docker.internal', // Allow Docker container access
        '.loca.lt',  // Allow all LocalTunnel domains
        '.ngrok.io', // Allow ngrok domains
        '.trycloudflare.com', // Allow Cloudflare tunnels
      ],
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          // Don't rewrite path - keep /api prefix
        },
      },
    };
  }

  return config;
});
