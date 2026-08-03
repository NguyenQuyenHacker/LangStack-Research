import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'

const ROOT = path.resolve(import.meta.dirname, '..')

/** Bo qua file rac / file rieng tu, khong dua vao sidebar */
const IGNORE_FILES = new Set(['..md', 'README.md'])

/** Bo tien to so o dau: "01-foundations" -> "foundations", "03-02-tools" -> "tools" */
function stripNumPrefix(name: string): string {
  return name.replace(/^(\d+-)+/, '')
}

/** "01-foundations" -> "Foundations" (so chi de sap thu tu, khong hien thi) */
function folderLabel(dirName: string): string {
  return stripNumPrefix(dirName)
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

/** Lay `title` trong frontmatter (khong kem so), khong co thi suy ra tu ten file */
function fileTitle(absPath: string, fileName: string): string {
  try {
    const fm = matter(fs.readFileSync(absPath, 'utf-8')).data as { title?: string }
    if (fm?.title) return fm.title
  } catch {
    /* file khong doc duoc thi rot xuong ten file */
  }
  // Fallback: "03-03-middleware-overview" -> "Middleware overview"
  const words = stripNumPrefix(fileName.replace(/\.md$/, '')).replace(/-/g, ' ')
  return words.charAt(0).toUpperCase() + words.slice(1)
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

/** File .md va thu muc con trong cung mot thu muc, sap theo ten (tien to so) chung mot day */
function entriesIn(dirAbs: string): { name: string; isDir: boolean }[] {
  if (!fs.existsSync(dirAbs)) return []
  return fs
    .readdirSync(dirAbs, { withFileTypes: true })
    .filter(
      (d) =>
        (d.isDirectory() && !d.name.startsWith('.') && d.name !== 'assets') ||
        (d.isFile() && d.name.endsWith('.md') && !IGNORE_FILES.has(d.name))
    )
    .map((d) => ({ name: d.name, isDir: d.isDirectory() }))
    .sort((a, b) => a.name.localeCompare(b.name))
}

type SidebarItem = { text: string; link?: string; collapsed?: boolean; items?: SidebarItem[] }

/**
 * Quet mot thu muc: file .md thanh item, thu muc con thanh group long nhau (de quy).
 * `dirAbs` la duong dan tuyet doi, `urlPrefix` la link URL tuong ung (vd /LangChain/03-harness).
 */
function itemsForDir(dirAbs: string, urlPrefix: string): SidebarItem[] {
  const items: SidebarItem[] = []

  for (const entry of entriesIn(dirAbs)) {
    if (entry.isDir) {
      const nested = itemsForDir(path.join(dirAbs, entry.name), `${urlPrefix}/${entry.name}`)
      if (nested.length) {
        items.push({ text: folderLabel(entry.name), collapsed: true, items: nested })
      }
    } else {
      items.push({
        text: fileTitle(path.join(dirAbs, entry.name), entry.name),
        link: `${urlPrefix}/${entry.name.replace(/\.md$/, '')}`
      })
    }
  }

  return items
}

/**
 * Sinh sidebar cho mot stack (LangChain / LangGraph / Langfuse).
 * Moi thu muc con thanh mot group long theo do sau bat ky, moi file .md thanh mot item.
 * Them file / folder moi vao repo la sidebar tu cap nhat, khong phai sua config.
 */
export function sidebarForStack(stack: string): SidebarItem[] {
  const stackAbs = path.join(ROOT, stack)
  const groups: SidebarItem[] = []

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
    const items = itemsForDir(path.join(stackAbs, dir), `/${stack}/${dir}`)
    if (items.length) {
      groups.push({ text: folderLabel(dir), collapsed: true, items })
    }
  }

  return groups
}
