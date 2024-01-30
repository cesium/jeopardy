import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "SEI ou não SEI",
  description: "SEI's gameshow",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>SEI ou não SEI</title>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className={`${inter.className} bg-primary text-white`}>
        {children}
      </body>
    </html>
  );
}
