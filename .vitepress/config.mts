import { defineConfig } from 'vitepress'
import { sidebarForStack, sidebarShared } from './sidebar.mts'

export default defineConfig({
  title: 'LangStack Research',
  description: 'Nghiên cứu LangChain / LangGraph / Langfuse — tiếng Việt, bám docs chính thức',
  lang: 'vi-VN',

  // Site chay o https://nguyenquyenhacker.github.io/LangStack-Research/
  // -> moi asset/link phai co tien to ten repo, doi ten repo la phai sua dong nay
  base: '/LangStack-Research/',

  // Toan bo repo la nguon markdown: file .md giu nguyen vi tri,
  // link tuong doi trong repo van chay ca tren GitHub lan tren site.
  srcExclude: [
    'README.md', // root README dung lam trang chu GitHub, site dung index.md
    '**/..md', // file rac ten la "..md"
    'note.md',
    'gitnote.md',
    'node_modules/**',
    '.prompts/**', // prompt dung vault, khong phai noi dung site
    '.claude/**' // cau hinh Claude Code
  ],

  // README.md cua moi stack lam trang index cua stack do -> /LangChain/ , /LangGraph/ ...
  rewrites: {
    'LangChain/README.md': 'LangChain/index.md',
    'LangGraph/README.md': 'LangGraph/index.md',
    'Langfuse/README.md': 'Langfuse/index.md'
  },

  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: true, // note dang draft, con nhieu link tro toi file chua viet

  markdown: {
    lineNumbers: true,
    image: { lazyLoading: true }
  },

  themeConfig: {
    outline: { level: [2, 3], label: 'Nội dung trang' },

    nav: [
      { text: 'LangChain', link: '/LangChain/' },
      { text: 'LangGraph', link: '/LangGraph/' },
      { text: 'Langfuse', link: '/Langfuse/' },
      {
        text: 'Quy ước',
        items: [
          { text: 'Conventions', link: '/CONVENTIONS' },
          { text: 'Glossary', link: '/GLOSSARY' }
        ]
      }
    ],

    // Sidebar sinh tu cay thu muc, khong phai khai bao tay tung file
    sidebar: {
      '/LangChain/': sidebarForStack('LangChain'),
      '/LangGraph/': sidebarForStack('LangGraph'),
      '/Langfuse/': sidebarForStack('Langfuse'),
      '/': sidebarShared()
    },

    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: 'Tìm kiếm', buttonAriaLabel: 'Tìm kiếm' },
          modal: {
            displayDetails: 'Hiện chi tiết',
            resetButtonTitle: 'Xoá tìm kiếm',
            backButtonTitle: 'Quay lại',
            noResultsText: 'Không có kết quả cho',
            footer: {
              selectText: 'chọn',
              navigateText: 'di chuyển',
              closeText: 'đóng'
            }
          }
        }
      }
    },

    docFooter: { prev: 'Trang trước', next: 'Trang sau' },
    lastUpdatedText: 'Cập nhật lần cuối',
    darkModeSwitchLabel: 'Giao diện',
    returnToTopLabel: 'Lên đầu trang',
    sidebarMenuLabel: 'Mục lục',

    socialLinks: [
      { icon: 'github', link: 'https://github.com/NguyenQuyenHacker/LangStack-Research' }
    ]
  }
})
