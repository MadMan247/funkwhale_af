import { useRouteQuery } from '@vueuse/router'
import { syncRef } from '@vueuse/core'
import { ref } from 'vue'

/**
 * Syncs ref `page` with the homonymous route query parameter
 * @returns {Ref<number>} The page number
 */
export default () => {
  const pageQuery = useRouteQuery<string>('page', '1')
  const page = ref<number>()
  syncRef(pageQuery, page, {
    transform: {
      ltr: (left) => +left,
      // TODO: Why toString?
      // @ts-expect-error string vs. number
      rtl: (right) => right.toString()
    }
  })

  return page
}
