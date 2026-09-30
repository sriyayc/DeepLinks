import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// Backend origin the /api proxy forwards to (same value used for SSR fetches).
const API_TARGET = process.env.API_BASE_URL || 'http://localhost:8000';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    // The frontend Dockerfile runs the Vite dev server. Vite blocks requests
    // whose Host header it does not recognise, which would reject Railway's
    // public *.up.railway.app domain. Allow all hosts so the hosted dev server
    // serves the workshop frontend. (Dev-server convenience only.)
    host: true,
    allowedHosts: true,
    // Proxy the backend API through the frontend origin so participants only
    // ever need the frontend URL (e.g. /api/orders/1 for the IDOR lab), and so
    // the shop session cookie is first-party. changeOrigin is required so
    // Railway routes the upstream request to the backend by its own hostname.
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true
      }
    }
  }
});
