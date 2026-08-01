import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: "/dashboard/hubspot",
        destination: "/dashboard/crm",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
