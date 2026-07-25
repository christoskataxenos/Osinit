/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darknet: {
          50: '#f5f3ff',
          500: '#8b5cf6',
          900: '#2e1065',
        }
      }
    },
  },
  plugins: [],
}
