import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Refer to https://github.com/tabler/tabler-icons/issues/1233
  // Without this alias, all the 5K icons are loaded on the page on initial load in HMR,
  // which leads to the development server crashing.
  resolve: {
    alias: {
      '@tabler/icons-react': '@tabler/icons-react/dist/esm/icons/index.mjs',
    },
  },
});
