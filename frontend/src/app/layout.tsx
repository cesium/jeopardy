import { Inter } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";

const sei = localFont({
  src: "fonts/TerminalGrotesque.ttf",
  variable: "--font-sei",
});
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const lava = localFont({
  src: "fonts/Pilowlava-Regular.otf",
  variable: "--font-lava",
});

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
      <body
        className={`${sei.variable} ${inter.variable} ${lava.variable} font-sei bg-background text-neutral-100 h-screen overflow-hidden`}
      >
        <video className="w-full h-full -z-10 absolute" autoPlay muted loop>
          <source src="/videos/estrelas.mp4" type="video/mp4" />
        </video>
        {children}
      </body>
    </html>
  );
}
