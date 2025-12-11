import type { NavigationGuardNext, RouteLocationNamedRaw, RouteLocationNormalized, RouteLocationRaw, RouteLocationResolvedGeneric } from 'vue-router'
import type { Permission } from '~/store/auth'
import { useRouter } from 'vue-router'

import useLogger from '~/composables/useLogger'
import store from '~/store'
import { TAURI_DEFAULT_INSTANCE_URL } from '~/store/instance'

const logger = useLogger()

const constraintPresets = {
  onlyOwnProfile: (to: RouteLocationResolvedGeneric) =>
    (!store.state.auth.authenticated || to.params.username !== store.state.auth.username)
      ? ({
        redirectTo: { name: 'profile.overview', params: to.params },
        isShowingLink: false
    }) : undefined,
  onlyMatchingDomain: (to: RouteLocationResolvedGeneric) =>
    (!store.state.auth.authenticated && to.query.domain && store.getters['instance/domain'] !== to.query.domain)
     ? ({
        redirectTo: { name: 'login', query: { next: to.fullPath } },
        isShowingLink: false
    }) : undefined
} as const

/** Add `...constraints('onlyOwnProfile', 'onlyMatchingDomain')` to your routes
 * @returns meta object with constraints array
 */
export const constraints = (...args: (keyof typeof constraintPresets)[]) => ({ constraints: args })

export const redirectOnConstraint = (to: RouteLocationNormalized, _: RouteLocationNormalized, next: NavigationGuardNext) => {
  console.log('CONSTRAINT redirectOnConstraint with `to`:', to)
  console.log('CONSTRAINT', 'auth', store.state.auth.authenticated, 'domain', to.query.domain, 'instance domain', store.getters['instance/domain'])

  const constraint = matchedConstraint(to)

  console.log('CONSTRAINT redirectOnConstraint constraint:', constraint)

  return constraint
    ? next(constraint.redirectTo)
    : next()
}

/**
 * @returns the first matched constraint (as defined in the statically declared `routes` object)
*/
export const matchedConstraint = (to: RouteLocationRaw | RouteLocationNormalized) => {
  const router = useRouter()

  const resolved = to instanceof Object && 'matched' in to
      ? to as RouteLocationResolvedGeneric
      : router.resolve(to)

    console.log('CONSTRAINT resolved:', resolved  ) //  matched routes do not contain any meta fields!

  return resolved.matched.flatMap(r =>
    ('meta' in r && 'constraints' in r.meta ? r.meta.constraints : []) as (keyof typeof constraintPresets)[]
  )
  .map(key => constraintPresets[key](resolved))
  .find(constraint => constraint !== undefined)
}

export const hasPermissions = (permission: Permission) => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (store.state.auth.authenticated && store.state.auth.availablePermissions[permission]) {
    return next()
  }

  logger.warn('Not authenticated. Redirecting to library.')
  next({ name: 'library.index' })
}

export const requireLoggedIn = (fallbackLocation?: RouteLocationNamedRaw) => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (store.state.auth.authenticated) return next()
  return next(fallbackLocation ?? { name: 'login', query: { next: to.fullPath } })
}

export const requireLoggedOut = (fallbackLocation: RouteLocationNamedRaw) => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (!store.state.auth.authenticated) return next()
  return next(fallbackLocation)
}

export const forceInstanceChooser = (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (to.path === '/instance-chooser') return next()

  // Force instance chooser if unset by tauri
  if (store.getters['instance/url'].href === TAURI_DEFAULT_INSTANCE_URL) {
    return next(`/instance-chooser?next=${encodeURIComponent(to.fullPath)}`)
  }

  return next()
}
