import { computed } from 'vue'
import { useRouter, type RouteLocationRaw, type LocationQuery } from 'vue-router'

type Assignment<T> = { on: (value : T | null) => string | null, isOn: (value: LocationQuery[string]) => boolean }

export const exactlyNull:Assignment<unknown> = ({ on: (_) => null, isOn: (value) => value === null })
export const notUndefined:Assignment<unknown> = ({ on: (_) => null, isOn: (value) => value !== undefined })

/**
 * Bind a modal to a single query parameter in the URL (and vice versa)
 *
 * @param flag query parameter to appear in the `url`, corresponding with `isOpen`
 * @param assignment a tuple of two functions:
 * - from outside world to flag value (default: (_) => null)
 * - from flag value to boolean (default: if flag value is null)
 *
 * This functionality completely independent from the `router` modules.
 */
export const useModal = <T> (
  flag: string,
  assignment: Assignment<T> = exactlyNull
) => {
  const router = useRouter()
  const query = computed(() =>
    router?.currentRoute.value ? router.currentRoute.value.query : {}
  )

  /**
   * Visibility of this modal
   *
   * Use this function to bind a modal to a query parameter in the URL.
   * Using this helper function will not change the routes.
   *
   * For example, if the modal flag is 'upload':
   *
   * ```vue
   * <template>
   *  <Modal :open="isOpen('upload')">...</Modal>
   * </template>
   * ```
   *
   * Url: `https://funkwhale.audio/?upload`
   *
   * More information on query flags: https://router.vuejs.org/api/type-aliases/LocationQueryValue.html
   *
   * Use `asAttribute` instead to bind a modal to an on/off attribute such as `aria-expanded` or `aria-pressed`
   *
   * @param flag Identifier for the modal
   * @returns a `ref`<boolean>
   */
  const isOpen = computed({
    get () {
      return flag in query.value && assignment.isOn(query.value[flag]!)
    },
    set (newValue: boolean) {
      router?.push({
        query: {
          ...query.value,
          [flag]: newValue ? assignment.on(null) : undefined
        }
      })
        .catch((err) => {
          throw new Error(`Problem pushing route query: ${err}.`)
        })
    }
  })

  /**
   * Current value of the flag in the URL, normalized to a string.
   *
   * Note that both `null` and `undefined` are coerced to an empty string, and arrays are joined with a space.
   *
   * Use in inputs.
   */
  const value = computed({
    get () {
      const flagValue = flag in query.value ? query.value[flag]! : ''
      return typeof flagValue === 'string' ? flagValue : flagValue === null ? '' : flagValue.join(' ')
    },
    set (newValue: string) {
      router?.push({
        query: {
          ...query.value,
          [flag]: newValue
        }
      })
        .catch((err) => {
          throw new Error(`Problem pushing route query: ${err}.`)
        })
    }
  })

  /**
   *
   * @param flag Identifier for the modal
   * @returns a `RouteLocationRaw` object to use in the `to` prop of a RouterLink component
   */
  const to: RouteLocationRaw = {
    query: { ...query.value, [flag]: null }
  }

  /**
   * Use this function to bind a modal to an on/off attribute such as `aria-expanded` or `aria-pressed`
   *
   * @param flag Identifier for the modal
   * @returns a `ref`<true | undefined>
   */
  const asAttribute = computed(() => isOpen.value || undefined)

  /**
   * Toggle the visibility of this modal
   *
   *
   * @param flag Identifier for the modal
   */
  const toggle = () => (isOpen.value = !isOpen.value)

  return { value, isOpen, to, asAttribute, toggle }
}

/* All possible useModals that produce a given `RouterLink` destination */
export const fromProps = <T>({ to } : { to?: RouteLocationRaw }, assignment: Assignment<T> = exactlyNull): ReturnType<typeof useModal>[] =>
  to && typeof to !== 'string' && 'query' in to && to.query
    ? Object.keys(to.query).map(k => useModal(k, assignment))
    : []
