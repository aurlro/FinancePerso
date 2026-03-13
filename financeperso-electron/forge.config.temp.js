module.exports = {
  "packagerConfig": {
    "asar": true,
    "asarUnpack": [
      "node_modules/better-sqlite3/**/*.node",
      "node_modules/better-sqlite3/**/*.dll",
      "node_modules/better-sqlite3/**/*.so",
      "node_modules/better-sqlite3/**/*.dylib"
    ]
  },
  "rebuildConfig": {
    "force": true
  },
  "makers": [
    {
      "name": "@electron-forge/maker-squirrel",
      "config": {}
    },
    {
      "name": "@electron-forge/maker-zip",
      "platforms": [
        "darwin"
      ]
    },
    {
      "name": "@electron-forge/maker-deb",
      "config": {}
    },
    {
      "name": "@electron-forge/maker-rpm",
      "config": {}
    }
  ],
  "plugins": [
    {
      "config": {
        "force": true
      },
      "_resolvedHooks": {},
      "name": "auto-unpack-natives"
    },
    {
      "name": "@electron-forge/plugin-vite",
      "config": {
        "build": [
          {
            "entry": "src/main.js",
            "config": "vite.main.config.mjs",
            "target": "main"
          },
          {
            "entry": "src/preload.js",
            "config": "vite.preload.config.mjs",
            "target": "preload"
          }
        ],
        "renderer": [
          {
            "name": "main_window",
            "config": "vite.renderer.config.mjs",
            "port": 3000
          }
        ]
      }
    },
    {
      "config": {
        "0": false,
        "1": false,
        "2": false,
        "3": false,
        "4": true,
        "5": true,
        "version": "1",
        "undefined": false
      },
      "_resolvedHooks": {},
      "name": "fuses",
      "fusesConfig": {
        "0": false,
        "1": false,
        "2": false,
        "3": false,
        "4": true,
        "5": true,
        "version": "1",
        "undefined": false
      }
    }
  ]
}