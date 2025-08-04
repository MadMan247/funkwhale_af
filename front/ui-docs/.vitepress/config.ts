import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Funkwhale UI',
  cleanUrls: true,
  cacheDir: './.vitepress/.vite',
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
      { text: 'Contributing', link: '/contributing' },
      {
        items: [
          { text: 'Activity', link: '/components/ui/activity' },
          { text: 'Alert', link: '/components/ui/alert' },
          { text: 'Card', link: '/components/ui/card' },
          {
            text: 'Navigation',
            link: '/navigation',
            items: [
              { text: 'Link', link: 'components/ui/link' },
              { text: 'Pagination', link: '/components/ui/pagination' },
              { text: 'Table of Contents', link: '/components/ui/toc' },
              { text: 'Tabs', link: '/components/ui/tabs' },
              { text: 'Nav', link: '/components/ui/nav' },
            ],
          },
          {
            text: 'Form',
            items: [
              {
                text: 'Button', link: '/components/ui/button',
                items: [
                  { text: 'Options Button', link: '/components/ui/button/options' },
                  { text: 'Play Button', link: '/components/ui/button/play' },
                ],
              },
              { text: 'Input', link: '/components/ui/input' },
              { text: 'Select', link: '/components/ui/select' },
              { text: 'Slider', link: '/components/ui/slider' },
              { text: 'Popover (Dropdown Menu)', link: '/components/ui/popover' },
              { text: 'Textarea', link: '/components/ui/textarea' },
              { text: 'Toggle', link: '/components/ui/toggle' },
            ],
          },
          { text: 'Heading', link: '/components/ui/heading' },
          {
            text: 'Layout', link: '/components/ui/layout/',
            items: [
              { text: "Spacer", link: "/components/ui/layout/spacer" },
              { text: "Header", link: "/components/ui/layout/header" },
              { text: "Section", link: "/components/ui/layout/section" },
              { text: "Table", link: "/components/ui/layout/table" },
              { text: "Using `flex`", link: "/components/ui/layout/flex" },
              { text: "Using `stack`", link: "/components/ui/layout/stack" },
              { text: "Using `grid`", link: "/components/ui/layout/grid" },
              { text: "Using `columns`", link: "/components/ui/layout/columns" },
            ]
          },
          { text: 'Loader', link: '/components/ui/loader' },
          { text: 'Modal', link: '/components/ui/modal' },
          { text: 'Pill',
            link: '/components/ui/pill',
            items: [
              { text: 'List of pills', link: '/components/ui/pills' }
            ]
          },
        ],
      },
    ],
    search: {
      provider: 'local',
    },
  },
})
