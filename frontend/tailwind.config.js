/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    colors: {
      primary: "#3089F0",
      secondary: "rgb(55, 142, 205)",
      lightgrey: "#F7F7F7",
      darkgrey: "#554B4B",
      white: "#FFFFFF",
      red:"#FF0000",
      black:"#000000",
    },
    extend: {
      boxShadow: {
        'top': 'inset 0px 6px 6px -6px rgba(0, 0, 0, 0.3)',
      },
    },
  },
  plugins: [],
};
