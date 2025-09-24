import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Configure API URL for production
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://igdb-api-d6xpjrmqsa-ew.a.run.app',
  },

  // Vercel-optimized settings
  compress: true,
  poweredByHeader: false,

  // Configure images for production
  images: {
    domains: ['images.igdb.com'],
    formats: ['image/webp', 'image/avif'],
  },
};

export default nextConfig;
