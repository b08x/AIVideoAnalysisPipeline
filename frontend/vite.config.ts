// vite.config.ts (Optimized for Bundle Analysis)
import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');

    return {
      define: {
        'import.meta.env.VITE_APP_API_URL': JSON.stringify(env.VITE_APP_API_URL),
        'import.meta.env.VITE_APP_WS_URL': JSON.stringify(env.VITE_APP_WS_URL),
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, './src'),
        }
      },
      server: {
        port: 5173,
        host: true,
        // Remove proxy - frontend will connect directly to backend
      },
      plugins: [
        react(),
        // Add the visualizer plugin only when in 'analysis' mode
        mode === 'analysis' ? visualizer({
            open: true, // Automatically open the report in your browser
            filename: 'stats.html', // Output file name
            gzipSize: true, // Show gzip size
            brotliSize: true, // Show brotli size
        }) : null,
      ],
      build: {
        // Vite automatically enables minification and other optimizations
        // for production builds, so we don't need to add much here.
        // This section is for any potential future overrides.
        rollupOptions: {
            output: {
                // Example of chunk splitting for larger apps:
                // manualChunks(id) {
                //   if (id.includes('node_modules')) {
                //     return 'vendor';
                //   }
                // }
            }
        }
      }
    };
});
