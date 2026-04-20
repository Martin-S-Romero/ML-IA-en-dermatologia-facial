/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{html,js}'
  ],
  theme: {
    extend: {
      colors: {
        // SkinAI design tokens
        forest:  '#233D30',
        bark:    '#B89A72',
        earth:   '#7A5C3A',
        cream:   '#FAF8F3',
        sand:    '#E8E2D6',
        mint:    '#C8E6D8',
        blush:   '#F0D5C8',
        rose:    '#C47060',
        slate:   '#5A6474',
        ink:     '#181C24',
        warn:    '#D4942A',
        ok:      '#2E7D5A',
        bg:      '#F0EDE6',
      },
      fontFamily: {
        display: ['"Fraunces"', 'serif'],
        body:    ['"DM Sans"', 'sans-serif'],
      },
      borderRadius: {
        card: '14px',
        sm:   '10px',
      },
      boxShadow: {
        card: '0 2px 16px rgba(24,28,36,0.07)',
        md:   '0 6px 32px rgba(24,28,36,0.11)',
        lg:   '0 12px 48px rgba(24,28,36,0.14)',
      },
      animation: {
        'fade-in':   'fadeIn 0.25s ease forwards',
        'pulse-dot': 'pulseDot 0.8s ease infinite alternate',
        'spin-ring': 'spinRing 1.2s linear infinite',
        'zone-pulse':'zonePulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn:    { from:{ opacity:'0', transform:'translateY(6px)' }, to:{ opacity:'1', transform:'none' } },
        pulseDot:  { to:{ opacity:'0.3' } },
        spinRing:  { to:{ transform:'rotate(360deg)' } },
        zonePulse: { '0%,100%':{ opacity:'1', transform:'scale(1)' }, '50%':{ opacity:'0.7', transform:'scale(1.04)' } },
      },
    },
  },
  plugins: [],
}
