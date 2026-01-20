/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // ✅ Mandatory for manual switching
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: { sans: ['Quicksand', 'sans-serif'] },
      borderRadius: { '4xl': '32px' }
    },
  },
  plugins: [],
}