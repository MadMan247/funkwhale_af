import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/content/libraries/tracks',
    component: () => import('~/views/content/Base.vue'),
    children: [{
      path: '',
      name: 'content.libraries.files',
      component: () => import('~/views/content/libraries/Files.vue'),
      props: route => ({ query: route.query.q })
    }]
  }
] as RouteRecordRaw[]
