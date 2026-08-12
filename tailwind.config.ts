import type { Config } from 'tailwindcss';
import bgPatterns from 'tailwindcss-bg-patterns';

const config: Config = {
  content: ['./Frontend/src/**/*.{js,ts,jsx,tsx,mdx}', './app/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        surface: '#000000',
        'surface-1': '#080808',
        'surface-2': '#0D0D0D',
        'surface-3': '#141414',
        'surface-hover': '#181818',
        accent: '#1693A7',
        'accent-hover': '#1BAFC5',
        'accent-active': '#117C8D',
        'accent-soft': 'rgba(22, 147, 167, 0.12)',
        'accent-border': 'rgba(22, 147, 167, 0.45)',
        muted: '#737373',
        'text-secondary': '#B3B3B3',
        'text-disabled': '#4A4A4A',
        border: '#222222',
        'border-hover': '#333333',
        'border-subtle': '#171717',
      },
      boxShadow: {
        soft: '0 20px 80px rgba(15, 23, 42, 0.08)',
      },
      backgroundImage: {
        'soft-gradient': 'radial-gradient(circle at top, rgba(255,255,255,0.6), transparent 45%)',
      },
    },
  },
  plugins: [bgPatterns],
};

export default config;
