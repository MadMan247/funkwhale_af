<script setup lang="ts">
import { type TabProps, TABS_INJECTION_KEY } from '~/injection-keys'
import { computed, provide, reactive, ref, watch } from 'vue'

import Button from '@ui/Button.vue'
import Link from '@ui/Link.vue'
import { useRoute } from 'vue-router'

const currentTitle = ref<TabProps['title']>('')
const tabs = reactive<TabProps[]>([])
const currentRoute = useRoute()

provide(TABS_INJECTION_KEY, {
  currentTitle,
  tabs
})

/* Note that this only compares the name. Make sure to add a `name` field to identify paths in your router config! */
const actualCurrentTitle = computed(() =>
  tabs.find(({ to }) => to && typeof to !== 'string' && 'name' in to && currentRoute.name === to?.name)?.title
  || currentTitle.value)

const currentIndex = computed(() =>
  tabs.findIndex(({ title }) => title === actualCurrentTitle.value)
)

// select first tab
watch(tabs, () => {
  if (tabs.length === 1) {
    currentTitle.value = tabs[0]!.title
  }
})
</script>

<template>
  <div class="funkwhale tabs">
    <!-- TODO: Either delete this component or integrate Nav which now implements all relevant features. This component is not accessible enough. -->
    <div class="tabs-header">
      <component
        :is="tab.to ? Link : Button"
        v-for="tab in tabs"
        :key="tab.title"
        ghost
        :class="{ 'is-active': actualCurrentTitle === tab.title }"
        v-bind="tab"
        :on-click="'to' in tab ? undefined : () => { currentTitle = tab.title }"
        class="tabs-item"
        @keydown.left="currentTitle = tabs[(currentIndex - 1 + tabs.length) % tabs.length]!.title"
        @keydown.right="currentTitle = tabs[(currentIndex + 1) % tabs.length]!.title"
      >
        <div class="is-spacing">
          {{ tab.title }}
        </div>
        <label>{{ tab.title }}</label>
      </component>

      <div class="tabs-right">
        <slot name="tabs-right" />
      </div>
    </div>

    <slot />
  </div>
</template>

<style lang="scss">
@use '~/style/funkwhale.scss';

.funkwhale.tabs {
    color: var(--fw-text-color);

    @include funkwhale.light-theme {
      --fw-border-color: var(--fw-gray-300);
    }

    @include funkwhale.dark-theme {
      --fw-text-color: var(--fw-gray-300);
      --fw-border-color: var(--fw-gray-700);
    }

    > .tabs-header {
      display: flex;
      align-items: end;
      padding-bottom: 8px;
      margin-bottom: 23px;
      border-bottom: 1px solid var(--fw-border-color);

      &:has(:focus-visible) {
        outline:1px dotted currentColor;
      }

      > .tabs-item {
        font-size: 1rem;
        padding: 8px;
        min-width: 96px;
        text-align: center;
        cursor: pointer;
        position: relative;
        font-weight: normal;
        border: none;
        background-color: transparent !important;

        &:hover {

          &::after {
            content: '';
            display: block;
            height: 4px;
            background-color: var(--fw-secondary);
            margin: 0 auto;
            width: calc(10% + 2rem);
            position: absolute;
            inset: auto 0 0px 0;
            border-radius: 100vh;
          }
        }

        .is-spacing {
            height: 0;
            visibility: hidden;
        }
        .is-icon {
          display: block;
          position: relative;
          transform: translateY(-.5rem);
          font-size: 1.5em;
          color: var(--fw-gray-500);
        }

        &.is-active, .is-spacing {
          font-weight: 900;

          &::after {
            content: '';
            display: block;
            height: 4px;
            background-color: var(--fw-secondary);
            margin: 0 auto;
            width: calc(10% + 2rem);
            position: absolute;
            inset: auto 0 0px 0;
            border-radius: 100vh;
          }
        }
      }

      > .tabs-right {
        margin-left: auto;
      }
    }
  }
</style>
