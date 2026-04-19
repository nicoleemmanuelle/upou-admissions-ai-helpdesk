/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        upou: {
          maroon: "#7B1113",
          gold: "#F4B400",
          ink: "#0B1220",
        },
      },
    },
  },
  plugins: [],
};

