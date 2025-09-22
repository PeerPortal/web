import type { NextConfig } from 'next';
import path from 'path';

/** @type {import('next').NextConfig} */
const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname),
  images: {
    domains: ['example.com', 'web-4w0h.onrender.com', 'localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**'
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000'
      }
    ]
  },
  transpilePackages: ['antd'],
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*'
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS'
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization'
          }
        ]
      }
    ];
  },
  async rewrites() {
    // Vercel 构建时 process.env.NEXT_PUBLIC_API_BASE_URL 可能未定义，需兜底处理
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiBase}/api/:path*`
      }
    ];
  }
};

export default nextConfig;
