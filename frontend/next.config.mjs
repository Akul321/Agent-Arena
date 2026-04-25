/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export so the backend can serve the built UI from disk.
  // The Dockerfile copies `out/` into the backend image.
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
