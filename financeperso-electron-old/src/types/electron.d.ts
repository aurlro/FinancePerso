/**
 * TypeScript definitions for Electron API exposed via preload script
 */

export interface ElectronAPI {
  getVersion(): Promise<string>
  getPath(name: string): Promise<string>
  platform: string
  ping(): string
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

export {}
