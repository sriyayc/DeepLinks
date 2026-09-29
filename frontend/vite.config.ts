import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    // The frontend Dockerfile runs the Vite dev server. Vite blocks requests
    // whose Host header it does not recognise, which would reject Railway's
    // public *.up.railway.app domain. Allow all hosts so the hosted dev server
    // serves the workshop frontend. (Dev-server convenience only.)
    host: true,
    allowedHosts: true
  }
});
