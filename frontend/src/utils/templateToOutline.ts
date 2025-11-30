import type { } from '@/types'

export function templateToOutline(structure: any, titleFallback = '未命名报告'): string {
  const name: string = structure?.['报告名称'] || titleFallback
  const sections: any[] = structure?.['章节结构'] || []
  const style: string = structure?.['风格要求'] || ''
  const rules: any = structure?.['格式规则'] || {}
  const dataReq: string[] = structure?.['数据要求'] || []

  const lines: string[] = []
  lines.push(`# ${name}`)
  if (style) lines.push(`\n> 风格要求：${style}`)
  if (rules && Object.keys(rules).length) {
    lines.push(`\n> 格式规则：`)
    Object.keys(rules).forEach(k => {
      const v = rules[k]
      lines.push(`> - ${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    })
  }
  if (dataReq && dataReq.length) {
    lines.push(`\n> 数据要求：`)
    dataReq.forEach(item => lines.push(`> - ${item}`))
  }

  if (!sections.length) {
    lines.push(`\n## 摘要`)
    lines.push(`\n（在此撰写摘要内容）`)
  } else {
    sections.forEach((sec, idx) => {
      const secName = sec['章节名'] || `章节${idx + 1}`
      const level = Number(sec['章节级别'] || 1)
      const prefix = '#'.repeat(Math.min(Math.max(level, 1), 6))
      lines.push(`\n${prefix} ${secName}`)
      const req = sec['内容要求']
      if (req) {
        lines.push(`\n- 要求：${req}`)
      }
      const words = sec['字数建议']
      if (words) {
        lines.push(`\n- 字数建议：${words}`)
      }
      lines.push(`\n（在此撰写本章节内容）`)
    })
  }

  return lines.join('\n')
}
