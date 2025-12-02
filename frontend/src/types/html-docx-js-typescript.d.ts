declare module 'html-docx-js-typescript' {
  export function asBlob(html: string, options?: {
    orientation?: 'portrait' | 'landscape'
    margins?: {
      top?: number
      right?: number
      bottom?: number
      left?: number
    }
  }): Promise<Blob>
}
