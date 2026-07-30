import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import DocMeta from './DocMeta.vue'
import ProgressTracker from './ProgressTracker.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  // Chen khoi metadata (doc_source / accessed / status) ngay duoi tieu de moi trang note
  Layout: () => h(DefaultTheme.Layout, null, {
    'doc-before': () => h(DocMeta),
    'aside-top': () => h(ProgressTracker)
  })
}
