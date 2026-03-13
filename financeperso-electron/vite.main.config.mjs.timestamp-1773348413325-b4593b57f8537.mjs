var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
  get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
}) : x)(function(x) {
  if (typeof require !== "undefined") return require.apply(this, arguments);
  throw Error('Dynamic require of "' + x + '" is not supported');
});

// vite.main.config.mjs
import { defineConfig } from "file:///Users/aurelien/Documents/Projets/FinancePerso/financeperso-electron/node_modules/vite/dist/node/index.js";
import path from "path";
var __vite_injected_original_dirname = "/Users/aurelien/Documents/Projets/FinancePerso/financeperso-electron";
var vite_main_config_default = defineConfig({
  build: {
    rollupOptions: {
      // Mark native modules as external - don't bundle them
      external: [
        "better-sqlite3",
        "electron-squirrel-startup",
        ...__require("module").builtinModules
      ]
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src"),
      "@electron": path.resolve(__vite_injected_original_dirname, "./electron")
    }
  }
});
export {
  vite_main_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5tYWluLmNvbmZpZy5tanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvYXVyZWxpZW4vRG9jdW1lbnRzL1Byb2pldHMvRmluYW5jZVBlcnNvL2ZpbmFuY2VwZXJzby1lbGVjdHJvblwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL1VzZXJzL2F1cmVsaWVuL0RvY3VtZW50cy9Qcm9qZXRzL0ZpbmFuY2VQZXJzby9maW5hbmNlcGVyc28tZWxlY3Ryb24vdml0ZS5tYWluLmNvbmZpZy5tanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL1VzZXJzL2F1cmVsaWVuL0RvY3VtZW50cy9Qcm9qZXRzL0ZpbmFuY2VQZXJzby9maW5hbmNlcGVyc28tZWxlY3Ryb24vdml0ZS5tYWluLmNvbmZpZy5tanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJztcbmltcG9ydCBwYXRoIGZyb20gJ3BhdGgnO1xuXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xuICBidWlsZDoge1xuICAgIHJvbGx1cE9wdGlvbnM6IHtcbiAgICAgIC8vIE1hcmsgbmF0aXZlIG1vZHVsZXMgYXMgZXh0ZXJuYWwgLSBkb24ndCBidW5kbGUgdGhlbVxuICAgICAgZXh0ZXJuYWw6IFtcbiAgICAgICAgJ2JldHRlci1zcWxpdGUzJyxcbiAgICAgICAgJ2VsZWN0cm9uLXNxdWlycmVsLXN0YXJ0dXAnLFxuICAgICAgICAuLi5yZXF1aXJlKCdtb2R1bGUnKS5idWlsdGluTW9kdWxlcyxcbiAgICAgIF0sXG4gICAgfSxcbiAgfSxcbiAgcmVzb2x2ZToge1xuICAgIGFsaWFzOiB7XG4gICAgICAnQCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYycpLFxuICAgICAgJ0BlbGVjdHJvbic6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL2VsZWN0cm9uJyksXG4gICAgfSxcbiAgfSxcbn0pO1xuIl0sCiAgIm1hcHBpbmdzIjogIjs7Ozs7Ozs7QUFBMFksU0FBUyxvQkFBb0I7QUFDdmEsT0FBTyxVQUFVO0FBRGpCLElBQU0sbUNBQW1DO0FBSXpDLElBQU8sMkJBQVEsYUFBYTtBQUFBLEVBQzFCLE9BQU87QUFBQSxJQUNMLGVBQWU7QUFBQTtBQUFBLE1BRWIsVUFBVTtBQUFBLFFBQ1I7QUFBQSxRQUNBO0FBQUEsUUFDQSxHQUFHLFVBQVEsUUFBUSxFQUFFO0FBQUEsTUFDdkI7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsT0FBTztBQUFBLE1BQ3BDLGFBQWEsS0FBSyxRQUFRLGtDQUFXLFlBQVk7QUFBQSxJQUNuRDtBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
