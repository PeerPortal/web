import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
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
  }
};

export default nextConfig;
