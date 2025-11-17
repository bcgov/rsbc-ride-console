/// <reference types="vitest" />
import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import { configDefaults } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';

const proxyObject = {
  target: 'http://localhost:8085',
  ws: true,
  changeOrigin: true,
  secure: false,
  timeout: 0,        // no timeout
  proxyTimeout: 0
};

// https://vitejs.dev/config/
export default defineConfig({
  // base: './',
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: "@import '@/assets/variables.scss';" // eslint-disable-line quotes
      }
    }
  },
  plugins: [vue(), vueJsx()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': proxyObject
    }
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx,vue}'],
    exclude: [...configDefaults.exclude, 'packages/template/*'],
    coverage: {
      provider: 'istanbul', // 'istanbul' or 'c8'
      reporter: ['text', 'json', 'html', 'clover', 'lcov']
    }
  }
});
