import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'

const ROOT = path.resolve(import.meta.dirname, '..')

/** Bo qua file rac / file rieng tu, khong dua vao sidebar */
const IGNORE_FILES = new Set(['..md', 'README.md'])

/** "01-foundations" -> "01 — Foundations" */
function folderLabel(dirName: string): string {
  const m = dirName.match(/^(\d+)-(.*)$/)
  const raw = m ? m[2] : dirName
  const words = raw
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
  return m ? `${m[1]} — ${words}` : words
}

/** Lay `title` trong frontmatter, khong co thi suy ra tu ten file */
function fileTitle(absPath: string, fileName: string): string {
  try {
    const fm = matter(fs.readFileSync(absPath, 'utf-8')).data as { title?: string }
    if (fm?.title) {
      const num = fileName.match(/^(\d+-\d+)/)
      return num ? `${num[1]} ${fm.title}` : fm.title
    }
  } catch {
    /* file khong doc duoc thi rot xuong ten file */
  }
  return fileName.replace(/\.md$/, '')
}

function mdFilesIn(dirAbs: string): string[] {
  if (!fs.existsSync(dirAbs)) return []
  return fs
    .readdirSync(dirAbs)
    .filter((f) => f.endsWith('.md') && !IGNORE_FILES.has(f))
    .sort()
}

function subDirsIn(dirAbs: string): string[] {
  if (!fs.existsSync(dirAbs)) return []
  return fs
    .readdirSync(dirAbs, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'assets')
    .map((d) => d.name)
    .sort()
}

/**
 * Sinh sidebar cho mot stack (LangChain / LangGraph / Langfuse).
 * Moi thu muc con thanh mot group, moi file .md thanh mot item.
 * Them file moi vao repo la sidebar tu cap nhat, khong phai sua config.
 */
export function sidebarForStack(stack: string) {
  const stackAbs = path.join(ROOT, stack)
  const groups: { text: string; collapsed: boolean; items: { text: string; link: string }[] }[] = []

  // File .md nam thang trong thu muc stack (README, SOURCES, ...)
  const rootItems = mdFilesIn(stackAbs).map((f) => ({
    text: fileTitle(path.join(stackAbs, f), f),
    link: `/${stack}/${f.replace(/\.md$/, '')}`
  }))
  if (fs.existsSync(path.join(stackAbs, 'README.md'))) {
    rootItems.unshift({ text: 'Mục lục', link: `/${stack}/` })
  }
  if (rootItems.length) {
    groups.push({ text: stack, collapsed: false, items: rootItems })
  }

  for (const dir of subDirsIn(stackAbs)) {
    const dirAbs = path.join(stackAbs, dir)
    const items = mdFilesIn(dirAbs).map((f) => ({
      text: fileTitle(path.join(dirAbs, f), f),
      link: `/${stack}/${dir}/${f.replace(/\.md$/, '')}`
    }))
    if (items.length) {
      groups.push({ text: folderLabel(dir), collapsed: true, items })
    }
  }

  return groups
}

/** Trang chung o root: CONVENTIONS, GLOSSARY */
export function sidebarShared() {
  return [
    {
      text: 'Quy ước chung',
      items: [
        { text: 'Conventions', link: '/CONVENTIONS' },
        { text: 'Glossary', link: '/GLOSSARY' }
      ]
    }
  ]
}
