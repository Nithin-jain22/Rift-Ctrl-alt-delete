/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        mist: '#f5f7fb',
        pulse: '#18c1ff',
        neon: '#19f79f',
        ember: '#ff6b6b',
      },
      boxShadow: {
        glow: '0 10px 30px rgba(24, 193, 255, 0.25)',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'ui-sans-serif', 'system-ui'],
        body: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui'],
      },
      backgroundImage: {
        haze: 'radial-gradient(circle at top, rgba(25, 247, 159, 0.15), transparent 55%), radial-gradient(circle at 15% 40%, rgba(24, 193, 255, 0.18), transparent 45%)',
      },
    },
  },
  plugins: [],
}
