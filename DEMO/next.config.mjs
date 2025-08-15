/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Configurações para Docker
  output: 'standalone',
  experimental: {
    outputFileTracingRoot: undefined,
  },
  // Configurações de produção
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
}

export default nextConfig
