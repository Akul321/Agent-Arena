/** @type {import('next').NextConfig} */
//
// The dashboard is a pure SPA — every API call goes to NEXT_PUBLIC_API_URL,
// nothing renders on the server, no API routes. So we always emit a static
// `out/` directory that any host can serve: Vercel as a static site, Render
// by baking it into the FastAPI image.
//
const nextConfig = {
  reactStrictMode: true,
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
