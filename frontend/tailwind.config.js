/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        background: "#04041c",
        primary: "#ffdb0d",
        accent: "#300bee",
      },
      fontFamily: {
        sei: ["var(--font-sei)"],
        inter: ["var(--font-inter)"],
        lava: ["var(--font-lava)"],
      },
    },
  },
  safelist: [
    {
      pattern: /grid-cols-(\d)/,
    },
  ],
  plugins: [],
};
