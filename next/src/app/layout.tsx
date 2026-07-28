"use client";

import { SessionProvider } from "next-auth/react";
import React, { useEffect } from "react";
import { QueryClientProvider } from "@tanstack/react-query";

import { Analytics } from "@vercel/analytics/react";
import { GoogleAnalytics } from "nextjs-google-analytics";
import { I18nextProvider } from "react-i18next";
import i18n from "../utils/i18n";
import { api, queryClient, trpcClient } from "../utils/api";

import "../styles/globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    document.documentElement.lang = i18n.language;
  }, []);

  return (
    <html lang="en">
      <body>
        <SessionProvider>
          <QueryClientProvider client={queryClient}>
            <api.Provider client={trpcClient} queryClient={queryClient}>
              <I18nextProvider i18n={i18n}>
                <GoogleAnalytics trackPageViews />
                <Analytics />
                {children}
              </I18nextProvider>
            </api.Provider>
          </QueryClientProvider>
        </SessionProvider>
      </body>
    </html>
  );
}
