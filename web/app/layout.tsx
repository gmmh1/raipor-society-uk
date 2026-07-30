import type { Metadata } from "next";
import { Instrument_Serif, Manrope, Noto_Sans_Bengali, Noto_Serif_Bengali } from "next/font/google";
import { getLang } from "@/lib/i18n/server";
import "./globals.css";

const display = Instrument_Serif({
  subsets: ["latin"],
  weight: ["400"],
  style: ["normal", "italic"],
  variable: "--font-display",
  display: "swap",
});

const body = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-body",
  display: "swap",
});

const bengaliDisplay = Noto_Serif_Bengali({
  subsets: ["bengali"],
  weight: ["500", "600", "700"],
  variable: "--font-bengali-display",
  display: "swap",
});

const bengaliBody = Noto_Sans_Bengali({
  subsets: ["bengali"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-bengali-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Raipor Society UK",
  description:
    "A community bringing people together through culture, learning, and collective progress — Unity, Culture, Friendship, Progress.",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const lang = await getLang();

  return (
    <html
      lang={lang}
      suppressHydrationWarning
      className={`${display.variable} ${body.variable} ${bengaliDisplay.variable} ${bengaliBody.variable}`}
    >
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "(function(){try{var t=localStorage.getItem('theme');if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();",
          }}
        />
        {children}
      </body>
    </html>
  );
}
