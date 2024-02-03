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
        primary: "#04041c",
        secondary: "#080836",
        accent: "#ff800d",
        test: "#2b09dc",
      },
      fontFamily: {
        sei: ["var(--font-sei)"],
        inter: ["var(--font-inter)"],
        lava: ["var(--font-lava)"],
      },
    },
  },
  plugins: [],
};
