<script setup lang="ts" generic="T extends 'tabs' | 'links'">
import { computed, useId, nextTick } from 'vue'
import { type RouterLinkProps, useRoute, useRouter } from 'vue-router'

import Link from '@ui/Link.vue'
import Button from '@ui/Button.vue'
import Layout from '@ui/Layout.vue'

// Tabs will lead to index positions (0, 1, 2 etc.) if it's tabs. Otherwise, their destinations needs to be specified.
type Tab = {
  title: string,
  icon?: string,
  badge?: string | number | false,
  to?: RouterLinkProps['to']
}

const tabs = defineModel<Tab[]>({ required: true })

/**
 * Use the `tabQueryField` prop and the `tabpanels` slot-prop to create accessible tabs.
 */
const props = defineProps<{
  tabQueryField?: string
}>()

const isTabs = !!props['tabQueryField']
const router = useRouter()
const route = useRoute()
const id = useId();

const currentIndex = computed(() => {
  if (isTabs) {
    const queryValue = route.query[props.tabQueryField as string]
    const indexString = Array.isArray(queryValue)
                ? queryValue[0] ?? '0'
                : queryValue ?? '0'
    return parseInt(indexString)
  }
  return tabs.value.findIndex(tab =>
      'to' in tab && tab.to && router.resolve(tab.to).path === route.path
    )
})

const navigateTo = ( index: number ) => {
  if (index<0) index = tabs.value.length-1
  if (index>tabs.value.length-1) index = 0

  if (isTabs) {
    router.replace({
    ...route,
      query: {
        ...route.query,
        [props.tabQueryField as string]: index
      }
    })
  } else {
    const targetTab = tabs.value[index];
    if (targetTab && targetTab.to) {
      router.replace(targetTab.to);
    }
  }

  nextTick(() => {
    document.getElementById(id+index+'tab')?.focus()
  })
}

const computedTabs = computed(() => tabs.value.map((tab, index) => ({
  ...tab,
  key: index,
  id: id+index+'tab',
  'aria-selected': currentIndex.value === index || undefined,
  tabindex: index === currentIndex.value ? 0 : -1,
  onKeydown: (e: KeyboardEvent) => {
    if (['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'].includes(e.key))
      e.preventDefault()
    if (['ArrowRight', 'ArrowDown'].includes(e.key))
      return navigateTo(index+1)
    if (['ArrowLeft', 'ArrowUp'].includes(e.key))
      return navigateTo(index-1)
    if (['Home'].includes(e.key))
      return navigateTo(0)
    if (['End'].includes(e.key))
      return navigateTo(Number.MAX_SAFE_INTEGER)
  },
  ...(isTabs ? ({
    role: 'tab',
    'aria-controls': id+index+'tabpanel',
    'aria-posinset': index + 1,
    'aria-setsize': tabs.value.length,
    'aria-pressed': undefined,
    '_____myIndex': index,
    '_____currentIndex': currentIndex.value,
    onClick: () => {
      navigateTo(index)
    }
  } ): ({
    to: 'to' in tab ? tab.to : ''
  } ))
} as const)
))

const tabpanels = computed(() => tabs.value.map((_, index) => ({
  'aria-labelledby':  id+index+'tab',
  role: 'tabpanel',
  id: id+index+'tabpanel',
  key: id+index,
  isActive: currentIndex.value === index
} as const )
))
</script>

<template>
  <Layout
    :id
    nav
    flex
    :role="isTabs ? 'tablist' : undefined"
    :class="$style.tablist"
  >
    <component
      :is="isTabs ? Button : Link"
      v-for="{ badge, ...tab } in computedTabs"
      v-bind="tab"
      :key="tab.key"
      :badge="isTabs && badge"
      ghost
      min-content
      :class="$style.tab"
    >
      <Layout
        stack
        no-gap
      >
        <span
          :class="$style.falseTitle"
          aria-hidden="true"
        >{{ tab.title }}</span>
        <span :class="$style.realTitle">{{ tab.title }}</span>
        <span
          v-if="badge && !isTabs"
          :class="$style.badge"
        >
          {{ badge }}
        </span>
      </Layout>
    </component>
  </Layout>
  <slot
    :current-index
    :tabpanels
  />
</template>

<style module>
.tablist {
    .realTitle {
        font-size: 16px;
        font-weight: 400;
    }

    .falseTitle[aria-hidden="true"] {
        font-size: 16px;
        font-weight: 900;
        opacity: 0;
        pointer-events: none;
        max-height: 0;
        overflow: hidden;
    }

    .tab {
        --hover-background-color: transparent;
        --exact-active-background-color: transparent;

        &:is([aria-selected], [aria-current]){
            .realTitle {
                font-weight: 900;

                &:after {
                    content: '';
                    display: block;
                    height: 4px;
                    background-color: var(--fw-secondary);
                    margin: 0 auto;
                    width: calc(10% + 2rem);
                    position: absolute;
                    inset: auto 0 -14px 0;
                    border-radius: 100vh;
                }
            }
        }
    }

    .badge {
        display: block;
        height: 16px;
        background-color: var(--fw-secondary);
        width: 16px;
        position: absolute;
        inset: -10px -14px auto auto;
        border-radius: 100vh;
        font-size: 10px;
        font-weight: 900;
        padding: 5px;
        line-height: 5px;
        color: var(--background-color);
    }
}
</style>
