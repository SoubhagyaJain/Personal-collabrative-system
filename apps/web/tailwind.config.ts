import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          950: '#0a0a0a',
          900: '#111111',
          500: '#e50914'
        }
      }
    }
  },
  plugins: []
};

export default config;
