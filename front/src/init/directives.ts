import type { InitModule } from '~/types'

export const install: InitModule = ({ app, store }) => {
  app.directive('title', function (el, binding) {
    store.commit('ui/pageTitle', binding.value)
  })
}
