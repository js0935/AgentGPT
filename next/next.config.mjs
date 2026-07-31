// @ts-check
/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation.
 * This is especially useful for Docker builds.
 */
!process.env.SKIP_ENV_VALIDATION && (await import("./src/env/server.mjs"));

/** @type {import("next").NextConfig} */
const config = {
  reactStrictMode: true,
  output: "standalone",
  webpack: function(config, options) {
    config.experiments = { asyncWebAssembly: true, layers: true };
    config.module.rules.push({
      test: /\.svg$/i,
      issuer: /\.[jt]sx?$/,
      use: ['@svgr/webpack'],
    })

    // 僅客戶端：依領域拆分 node_modules vendor chunk。
    // 讓首頁不必載入 PDF / markdown 等非首頁套件，且跨頁面共享的套件只打包一份。
    // 保留 Next.js 既有 cacheGroups（framework 優先權 40 不受影響）。
    if (!options.isServer) {
      const splitChunks = config.optimization && config.optimization.splitChunks;
      config.optimization.splitChunks = {
        ...splitChunks,
        cacheGroups: {
          ...(splitChunks && splitChunks.cacheGroups),
          "vendor-pdf": {
            test: /[\\/]node_modules[\\/]@react-pdf[\\/]/,
            name: "vendor-pdf",
            chunks: "all",
            priority: 35,
            enforce: true,
          },
          "vendor-markdown": {
            test: /[\\/]node_modules[\\/](react-markdown|remark-gfm|rehype-highlight|highlight\.js|lowlight|unified|micromark|mdast-util-|hast-util-|unist-util-)[\\/]/,
            name: "vendor-markdown",
            chunks: "all",
            priority: 35,
            enforce: true,
          },
          "vendor-common": {
            test: /[\\/]node_modules[\\/]/,
            name: "vendor-common",
            chunks: "async",
            minChunks: 2,
            priority: 25,
          },
        },
      };
    }
    return config;
  },
};

export default config;
