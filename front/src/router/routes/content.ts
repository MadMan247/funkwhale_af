import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/content',
    component: () => import('~/views/content/Base.vue'),
    children: [{
      path: '',
      name: 'content.index',
      component: () => import('~/views/content/Home.vue')
    }]
  },
  {
    path: '/content/libraries/tracks',
    component: () => import('~/views/content/Base.vue'),
    children: [{
      path: '',
      name: 'content.libraries.files',
      component: () => import('~/views/content/libraries/Files.vue'),
      props: route => ({ query: route.query.q })
    }]
  },
  {
    path: '/content/libraries',
    component: () => import('~/views/content/Base.vue'),
    children: [{
      path: '',
      name: 'content.libraries.index',
      component: () => import('~/views/content/libraries/Home.vue')
    }]
  }
] as RouteRecordRaw[]
