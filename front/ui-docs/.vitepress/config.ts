import { defineConfig } from 'vitepress'
import { fileURLToPath, URL } from 'node:url'
import { tasklist } from "@mdit/plugin-tasklist"

export default defineConfig({
  title: 'Funkwhale UI',
  cleanUrls: true,
  cacheDir: './.vitepress/.vite',
  markdown: {
    lineNumbers: true,
    config: (md) => {
      md.use(tasklist);
    }
  },
  themeConfig: {
    nav: [
      { text: 'Home', link: 'https://funkwhale.audio' },
      { text: 'Gitlab', link: 'https://dev.funkwhale.audio/funkwhale/ui' },
    ],
    sidebar: [
      { text: 'Designing Pages', link: '/designing-pages' },
      { text: 'Using Color', link: '/using-color' },
      { text: 'Using Width', link: '/using-width' },
      { text: 'Using Alignment', link: '/using-alignment' },
      { text: 'Using Components', link: '/using-components' },
      { text: 'Maintaining Accessibility', link: '/maintaining-accessibility' },
      { text: 'Contributing', link: '/contributing' },
      {
        items: [
          { text: 'Alert', link: '/components/ui/alert' },
          { text: 'Button', link: '/components/ui/button',
            items: [
              { text: 'Options Button', link: '/components/ui/button/options' },
              { text: 'Play Button', link: '/components/ui/button/play' },
            ],
          },
          { text: 'Card', link: '/components/ui/card' },
          {
            text: 'Forms', link: '/forms',
            items: [
              { text: 'Input', link: '/components/ui/input' },
              {
                text: 'Pill',
                link: '/components/ui/pill',
                items: [
                  { text: 'List of pills', link: '/components/ui/pills' }
                ]
              },
              { text: 'Select', link: '/components/ui/select' },
              { text: 'Slider', link: '/components/ui/slider' },
              { text: 'Textarea', link: '/components/ui/textarea' },
              { text: 'Toggle', link: '/components/ui/toggle' },
            ],
          },
          { text: 'Heading', link: '/components/ui/heading' },
          {
            text: 'Layout', link: '/components/ui/layout/',
            items: [
              { text: "Header", link: "/components/ui/layout/header" },
              { text: "Section", link: "/components/ui/layout/section" },
              { text: "Spacer", link: "/components/ui/layout/spacer" },
              { text: "Table", link: "/components/ui/layout/table" },
              { text: "Using `columns`", link: "/components/ui/layout/columns" },
              { text: "Using `flex`", link: "/components/ui/layout/flex" },
              { text: "Using `grid`", link: "/components/ui/layout/grid" },
              { text: "Using `stack`", link: "/components/ui/layout/stack" },
            ]
          },
          { text: 'Loader', link: '/components/ui/loader' },
          {
            text: 'Navigation', link: '/navigation',
            items: [
              { text: 'Link', link: '/components/ui/link' },
              { text: 'Modal', link: '/components/ui/modal' },
              { text: 'Nav', link: '/components/ui/nav' },
              { text: 'Pagination', link: '/components/ui/pagination' },
              { text: 'Table of Contents', link: '/components/ui/toc' },
              { text: 'Tabs', link: '/components/ui/tabs' },
            ],
          },
          { text: 'Popover (Dropdown Menu)', link: '/components/ui/popover' },
        ],
      },
    ],
    search: {
      provider: 'local',
    },
  },
  vite: {
    resolve: {
      alias: [
        {
          find: /^~\/(.*)/,
          replacement: fileURLToPath(
            new URL('../../src/$1', import.meta.url),
          ),
        },
        {
          find: /^@ui\/(.*)/,
          replacement: fileURLToPath(
            new URL('../../src/components/ui/$1', import.meta.url),
          ),
        },
      ],
    },
  },
})
