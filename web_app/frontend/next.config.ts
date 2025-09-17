import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',

  // Configure API URL for production
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },

  // Optimize for production
  compress: true,
  poweredByHeader: false,

  // Configure images for production
  images: {
    domains: ['images.igdb.com'],
    formats: ['image/webp', 'image/avif'],
  },
};

export default nextConfig;
