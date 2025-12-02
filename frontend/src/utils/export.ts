/**
 * 报告导出工具
 * 支持导出为 Markdown、HTML、Word、PDF 格式
 */

import { saveAs } from 'file-saver'

// Markdown 转 HTML 的简单实现（Vditor 已内置，这里作为备用）
const markdownToHtml = (markdown: string): string => {
  // 基础转换，实际使用时可以用 Vditor 的 getHTML()
  let html = markdown
    // 标题
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // 粗体和斜体
    .replace(/\*\*\*(.*?)\*\*\*/gim, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    // 链接和图片
    .replace(/!\[(.*?)\]\((.*?)\)/gim, '<img alt="$1" src="$2" />')
    .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2">$1</a>')
    // 代码块
    .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
    .replace(/`(.*?)`/gim, '<code>$1</code>')
    // 引用
    .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
    // 列表
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    // 分割线
    .replace(/^---$/gim, '<hr />')
    // 换行
    .replace(/\n/gim, '<br />')

  return html
}

// 生成带样式的 HTML 文档
const generateStyledHtml = (content: string, title: string): string => {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.8;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
      background: #fff;
    }
    h1 { font-size: 2em; margin: 1em 0 0.5em; color: #1a1a1a; border-bottom: 2px solid #409eff; padding-bottom: 0.3em; }
    h2 { font-size: 1.5em; margin: 1em 0 0.5em; color: #2c3e50; }
    h3 { font-size: 1.25em; margin: 1em 0 0.5em; color: #34495e; }
    p { margin: 0.8em 0; text-align: justify; }
    a { color: #409eff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em; }
    pre { background: #f8f8f8; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 1em 0; }
    pre code { background: none; padding: 0; }
    blockquote { border-left: 4px solid #409eff; padding-left: 16px; margin: 1em 0; color: #666; background: #f9f9f9; padding: 12px 16px; }
    ul, ol { margin: 0.8em 0; padding-left: 2em; }
    li { margin: 0.4em 0; }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; }
    th, td { border: 1px solid #ddd; padding: 10px 12px; text-align: left; }
    th { background: #f5f5f5; font-weight: 600; }
    tr:nth-child(even) { background: #fafafa; }
    img { max-width: 100%; height: auto; border-radius: 4px; margin: 1em 0; }
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 2em 0; }
    .title-page { text-align: center; padding: 60px 0; border-bottom: 1px solid #eee; margin-bottom: 40px; }
    .title-page h1 { border: none; font-size: 2.5em; }
    .title-page .date { color: #888; margin-top: 20px; }
    @media print {
      body { padding: 0; max-width: none; }
      .title-page { page-break-after: always; }
    }
  </style>
</head>
<body>
  <div class="title-page">
    <h1>${title}</h1>
    <p class="date">生成时间：${new Date().toLocaleString('zh-CN')}</p>
  </div>
  <div class="content">
    ${content}
  </div>
</body>
</html>`
}

/**
 * 导出为 Markdown 文件
 */
export const exportToMarkdown = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  saveAs(blob, `${filename}.md`)
}

/**
 * 导出为纯文本文件
 */
export const exportToText = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  saveAs(blob, `${filename}.txt`)
}

/**
 * 导出为 HTML 文件
 */
export const exportToHtml = (htmlContent: string, title: string, filename: string) => {
  const fullHtml = generateStyledHtml(htmlContent, title)
  const blob = new Blob([fullHtml], { type: 'text/html;charset=utf-8' })
  saveAs(blob, `${filename}.html`)
}

/**
 * 导出为 Word 文档 (.docx)
 * 使用 html-docx-js-typescript 库
 */
export const exportToWord = async (htmlContent: string, title: string, filename: string) => {
  try {
    // 动态导入以减少初始包大小
    const { asBlob } = await import('html-docx-js-typescript')
    
    const fullHtml = generateStyledHtml(htmlContent, title)
    const blob = await asBlob(fullHtml) as Blob
    saveAs(blob, `${filename}.docx`)
    return true
  } catch (error) {
    console.error('导出 Word 失败:', error)
    // 降级为 HTML 导出
    exportToHtml(htmlContent, title, filename)
    return false
  }
}

/**
 * 导出为 PDF（使用浏览器打印功能）
 */
export const exportToPdf = (htmlContent: string, title: string) => {
  const fullHtml = generateStyledHtml(htmlContent, title)
  
  // 创建隐藏的 iframe
  const iframe = document.createElement('iframe')
  iframe.style.position = 'fixed'
  iframe.style.right = '0'
  iframe.style.bottom = '0'
  iframe.style.width = '0'
  iframe.style.height = '0'
  iframe.style.border = 'none'
  document.body.appendChild(iframe)
  
  const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document
  if (iframeDoc) {
    iframeDoc.open()
    iframeDoc.write(fullHtml)
    iframeDoc.close()
    
    // 等待内容加载完成后打印
    setTimeout(() => {
      iframe.contentWindow?.focus()
      iframe.contentWindow?.print()
      
      // 打印完成后移除 iframe
      setTimeout(() => {
        document.body.removeChild(iframe)
      }, 1000)
    }, 500)
  }
}

/**
 * 导出选项类型
 */
export type ExportFormat = 'markdown' | 'text' | 'html' | 'word' | 'pdf'

/**
 * 统一导出接口
 */
export const exportReport = async (
  format: ExportFormat,
  content: string,
  htmlContent: string,
  title: string,
  filename: string
): Promise<boolean> => {
  try {
    switch (format) {
      case 'markdown':
        exportToMarkdown(content, filename)
        break
      case 'text':
        exportToText(content, filename)
        break
      case 'html':
        exportToHtml(htmlContent, title, filename)
        break
      case 'word':
        await exportToWord(htmlContent, title, filename)
        break
      case 'pdf':
        exportToPdf(htmlContent, title)
        break
      default:
        throw new Error(`不支持的导出格式: ${format}`)
    }
    return true
  } catch (error) {
    console.error('导出失败:', error)
    return false
  }
}
