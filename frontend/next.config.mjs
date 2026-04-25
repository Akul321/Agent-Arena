/** @type {import('next').NextConfig} */
//
// Two build modes:
//
// - STATIC_EXPORT=1  → produces a static `out/` directory. Used by the
//   Dockerfile so FastAPI can serve the UI from disk (single-container
//   Render deploy).
//
// - Anything else    → standard Next.js build to `.next/`. Used by Vercel,
//   which hosts Next.js natively.
//
const staticExport = process.env.STATIC_EXPORT === "1";

const nextConfig = {
  reactStrictMode: true,
  ...(staticExport
    ? {
        output: "export",
        trailingSlash: true,
        images: { unoptimized: true },
      }
    : {}),
};

export default nextConfig;
