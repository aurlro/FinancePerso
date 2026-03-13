# Assets

## Icônes requises pour le packaging:

- `icon.icns` - macOS (512x512, 1024x1024)
- `icon.ico` - Windows (256x256, 128x128, 64x64, 32x32, 16x16)
- `icon.png` - Linux (512x512)

## Génération:

Utilisez electron-icon-builder ou convertissez depuis un PNG:
```bash
npm install -g electron-icon-builder
electron-icon-builder --input=./icon.png --output=./assets
```

Ou manuellement avec ImageMagick:
```bash
# macOS
iconutil -c icns icon.iconset

# Windows
convert icon.png -define icon:auto-resize=256,128,64,32,16 icon.ico
```
