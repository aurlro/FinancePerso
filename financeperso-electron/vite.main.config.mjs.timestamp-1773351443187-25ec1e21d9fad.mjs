// vite.main.config.mjs
import { defineConfig } from "file:///Users/aurelien/Documents/Projets/FinancePerso/financeperso-electron/node_modules/vite/dist/node/index.js";
import path from "path";
import { builtinModules } from "module";
import copy from "file:///Users/aurelien/Documents/Projets/FinancePerso/financeperso-electron/node_modules/rollup-plugin-copy/dist/index.commonjs.js";
var __vite_injected_original_dirname = "/Users/aurelien/Documents/Projets/FinancePerso/financeperso-electron";
var vite_main_config_default = defineConfig({
  build: {
    rollupOptions: {
      // Mark native modules as external - don't bundle them
      external: [
        "better-sqlite3",
        "electron-squirrel-startup",
        "csv-parse",
        "csv-parse/sync",
        ...builtinModules,
        ...builtinModules.map((m) => `node:${m}`)
      ],
      plugins: [
        copy({
          targets: [
            { src: "electron/services/*", dest: ".vite/build/electron/services" }
          ],
          hook: "writeBundle"
        })
      ]
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src")
    }
  }
});
export {
  vite_main_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5tYWluLmNvbmZpZy5tanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvYXVyZWxpZW4vRG9jdW1lbnRzL1Byb2pldHMvRmluYW5jZVBlcnNvL2ZpbmFuY2VwZXJzby1lbGVjdHJvblwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL1VzZXJzL2F1cmVsaWVuL0RvY3VtZW50cy9Qcm9qZXRzL0ZpbmFuY2VQZXJzby9maW5hbmNlcGVyc28tZWxlY3Ryb24vdml0ZS5tYWluLmNvbmZpZy5tanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL1VzZXJzL2F1cmVsaWVuL0RvY3VtZW50cy9Qcm9qZXRzL0ZpbmFuY2VQZXJzby9maW5hbmNlcGVyc28tZWxlY3Ryb24vdml0ZS5tYWluLmNvbmZpZy5tanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJztcbmltcG9ydCBwYXRoIGZyb20gJ3BhdGgnO1xuaW1wb3J0IHsgYnVpbHRpbk1vZHVsZXMgfSBmcm9tICdtb2R1bGUnO1xuaW1wb3J0IGNvcHkgZnJvbSAncm9sbHVwLXBsdWdpbi1jb3B5JztcblxuLy8gaHR0cHM6Ly92aXRlanMuZGV2L2NvbmZpZ1xuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgYnVpbGQ6IHtcbiAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICAvLyBNYXJrIG5hdGl2ZSBtb2R1bGVzIGFzIGV4dGVybmFsIC0gZG9uJ3QgYnVuZGxlIHRoZW1cbiAgICAgIGV4dGVybmFsOiBbXG4gICAgICAgICdiZXR0ZXItc3FsaXRlMycsXG4gICAgICAgICdlbGVjdHJvbi1zcXVpcnJlbC1zdGFydHVwJyxcbiAgICAgICAgJ2Nzdi1wYXJzZScsXG4gICAgICAgICdjc3YtcGFyc2Uvc3luYycsXG4gICAgICAgIC4uLmJ1aWx0aW5Nb2R1bGVzLFxuICAgICAgICAuLi5idWlsdGluTW9kdWxlcy5tYXAobSA9PiBgbm9kZToke219YCksXG4gICAgICBdLFxuICAgICAgcGx1Z2luczogW1xuICAgICAgICBjb3B5KHtcbiAgICAgICAgICB0YXJnZXRzOiBbXG4gICAgICAgICAgICB7IHNyYzogJ2VsZWN0cm9uL3NlcnZpY2VzLyonLCBkZXN0OiAnLnZpdGUvYnVpbGQvZWxlY3Ryb24vc2VydmljZXMnIH0sXG4gICAgICAgICAgXSxcbiAgICAgICAgICBob29rOiAnd3JpdGVCdW5kbGUnLFxuICAgICAgICB9KSxcbiAgICAgIF0sXG4gICAgfSxcbiAgfSxcbiAgcmVzb2x2ZToge1xuICAgIGFsaWFzOiB7XG4gICAgICAnQCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYycpLFxuICAgIH0sXG4gIH0sXG59KTtcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBMFksU0FBUyxvQkFBb0I7QUFDdmEsT0FBTyxVQUFVO0FBQ2pCLFNBQVMsc0JBQXNCO0FBQy9CLE9BQU8sVUFBVTtBQUhqQixJQUFNLG1DQUFtQztBQU16QyxJQUFPLDJCQUFRLGFBQWE7QUFBQSxFQUMxQixPQUFPO0FBQUEsSUFDTCxlQUFlO0FBQUE7QUFBQSxNQUViLFVBQVU7QUFBQSxRQUNSO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQSxHQUFHO0FBQUEsUUFDSCxHQUFHLGVBQWUsSUFBSSxPQUFLLFFBQVEsQ0FBQyxFQUFFO0FBQUEsTUFDeEM7QUFBQSxNQUNBLFNBQVM7QUFBQSxRQUNQLEtBQUs7QUFBQSxVQUNILFNBQVM7QUFBQSxZQUNQLEVBQUUsS0FBSyx1QkFBdUIsTUFBTSxnQ0FBZ0M7QUFBQSxVQUN0RTtBQUFBLFVBQ0EsTUFBTTtBQUFBLFFBQ1IsQ0FBQztBQUFBLE1BQ0g7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsT0FBTztBQUFBLElBQ3RDO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
