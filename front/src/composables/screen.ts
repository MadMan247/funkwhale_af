import {
  type MaybeRefOrGetter,
  createGlobalState,
  toValue,
  useWindowSize
} from '@vueuse/core'
import { computed } from 'vue'

const MOBILE_WIDTH = 640

export const useScreenSize = createGlobalState(() =>
  useWindowSize({ includeScrollbar: false })
)
export const isMobileView = (
  width: MaybeRefOrGetter<number> = useScreenSize().width
) =>
  computed(() => (toValue(width) ?? Number.POSITIVE_INFINITY) <= MOBILE_WIDTH)
