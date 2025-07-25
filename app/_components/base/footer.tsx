import Logo from '@/components/base/logo';
import Link from 'next/link';
import { Globe, Mail, Phone, MapPin } from 'lucide-react';

const footerLinks = {
  services: [
    { href: '/tutor', label: '导师服务' },
    { href: '/', label: '申请咨询' },
    { href: '/', label: '文书修改' },
    { href: '/', label: '面试辅导' }
  ],
  resources: [
    { href: '/', label: '申请指南' },
    { href: '/', label: '院校信息' },
    { href: '/', label: '专业解析' },
    { href: '/', label: '成功案例' }
  ],
  company: [
    { href: '/', label: '关于我们' },
    { href: '/', label: '联系我们' },
    { href: '/', label: '隐私政策' },
    { href: '/', label: '服务条款' }
  ]
};

export default function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <div className="py-12">
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
            {/* Brand section */}
            <div className="space-y-4">
              <Link href="/" className="flex items-center gap-2">
                <Logo size={32} />
                <span className="text-xl font-bold">PeerPortal</span>
              </Link>
              <p className="text-muted-foreground text-sm">
                留学申请一站式平台，为您的留学之路提供专业指导与支持。
              </p>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Globe size={16} />
                <span>全球留学服务</span>
              </div>
            </div>

            {/* Services */}
            <div className="space-y-4">
              <h3 className="font-semibold">服务项目</h3>
              <ul className="space-y-2">
                {footerLinks.services.map((link, index) => (
                  <li key={index}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-4">
              <h3 className="font-semibold">资源中心</h3>
              <ul className="space-y-2">
                {footerLinks.resources.map((link, index) => (
                  <li key={index}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company & Contact */}
            <div className="space-y-4">
              <h3 className="font-semibold">公司信息</h3>
              <ul className="space-y-2">
                {footerLinks.company.map((link, index) => (
                  <li key={index}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
              <div className="space-y-2 pt-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Mail size={16} />
                  <span>contact@peerportal.com</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Phone size={16} />
                  <span>+1 (555) 123-4567</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom section */}
        <div className="border-t py-6">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <p className="text-sm text-muted-foreground">
              © 2024 PeerPortal. 保留所有权利。
            </p>
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                中文
              </Link>
              <span className="text-muted-foreground">|</span>
              <Link
                href="/"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                English
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
