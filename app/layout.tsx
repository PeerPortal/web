import type { Metadata } from 'next';
import localFont from 'next/font/local';
import './globals.css';
import Navbar from '@/components/base/navbar';
import Footer from '@/components/base/footer';
import { NuqsAdapter } from 'nuqs/adapters/next/app';
import { AuthInitializer } from '@/components/auth/auth-initializer';
import ChatWidget from '@/components/ui/chat-widget';
import LocaleProvider from '@/components/i18n/LocaleProvider';
import LanguageSwitcher from '@/components/ui/language-switcher';
import { FirstVisitModal } from '@/components/first-visit/first-visit-modal';
import { ConfigProvider } from 'antd';
import antdTheme from '@/lib/antd-theme';
import StyledComponentsRegistry from '@/lib/AntdRegistry';


const geistSans = localFont({
  src: '../fonts/GeistVariableVF.woff2',
  variable: '--font-geist-sans',
  display: 'swap'
});

const geistMono = localFont({
  src: '../fonts/GeistMonoVariableVF.woff2',
  variable: '--font-geist-mono',
  display: 'swap'
});

export const metadata: Metadata = {
  title: 'OfferIn',
  description: 'OfferIn 留学 - 留学申请一站式平台',
  icons: {
    icon: '/icon.png'
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <StyledComponentsRegistry>
          <ConfigProvider theme={antdTheme} wave={{ disabled: true }}>
            <LocaleProvider>
              <AuthInitializer>
                <Navbar />
                <NuqsAdapter>{children}</NuqsAdapter>
                <Footer />
                <ChatWidget />
                <LanguageSwitcher />
                <FirstVisitModal />
              </AuthInitializer>
            </LocaleProvider>
          </ConfigProvider>
        </StyledComponentsRegistry>
      </body>
    </html>
  );
}
