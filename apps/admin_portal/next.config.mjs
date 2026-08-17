/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/auth/:path*',
        destination: 'http://127.0.0.1:8003/api/v1/auth/:path*'
      },
      {
        source: '/api/v1/organizations/:path*',
        destination: 'http://127.0.0.1:8001/api/v1/organizations/:path*'
      },
      {
        source: '/api/v1/departments/:path*',
        destination: 'http://127.0.0.1:8001/api/v1/departments/:path*'
      },
      {
        source: '/api/v1/business-rules/:path*',
        destination: 'http://127.0.0.1:8001/api/v1/business-rules/:path*'
      },
      {
        source: '/api/v1/voice-config',
        destination: 'http://127.0.0.1:8001/api/v1/voice-config'
      },
      {
        source: '/api/v1/knowledge/:path*',
        destination: 'http://127.0.0.1:8002/api/v1/knowledge/:path*'
      },
      {
        source: '/api/v1/calls/:path*',
        destination: 'http://127.0.0.1:8003/api/v1/calls/:path*'
      },
      {
        source: '/internal/:path*',
        destination: 'http://127.0.0.1:8003/internal/:path*'
      },
      {
        source: '/api/v1/engine/:path*',
        destination: 'http://127.0.0.1:8000/:path*'
      }
    ];
  }
};

export default nextConfig;
