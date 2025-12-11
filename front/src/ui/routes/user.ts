import type { RouteRecordRaw } from 'vue-router'
import { constraints, redirectOnConstraint } from '~/router/guards'

export default [
  { suffix: '.full', path: '@:username@:domain' },
  { suffix: '', path: '@:username' }
].map(route => {
  return {
    path: route.path,
    name: `profile${route.suffix}`,
    component: () => import('~/views/auth/ProfileBase.vue'),
    props: true,
    beforeEnter: redirectOnConstraint,
    children: [{
        path: '',
        name: `profile${route.suffix}.overview`,
        component: () => import('~/views/auth/ProfileOverview.vue'),
        meta: constraints('onlyMatchingDomain')
      },
      {
        path: 'activity',
        name: `profile${route.suffix}.activity`,
        component: () => import('~/views/auth/ProfileActivity.vue'),
        meta: constraints('onlyMatchingDomain')
      },
      {
        path: 'manageUploads',
        name: `profile${route.suffix}.manageUploads`,
        component: () => import('~/views/auth/ManageUploads.vue'),
        meta: constraints('onlyOwnProfile', 'onlyMatchingDomain')
      }
    ]
  }
}) satisfies RouteRecordRaw[]
