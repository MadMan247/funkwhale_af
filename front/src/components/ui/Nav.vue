<script setup lang="ts">
import { type RouterLinkProps } from 'vue-router'

import Link from '~/components/ui/Link.vue'
import Layout from '~/components/ui/Layout.vue'

type Tab = {
    title: string,
    to: RouterLinkProps['to'],
    icon?: string,
    badge?: string | number
}

const tabs = defineModel<Tab[]>({ required: true })
</script>

<template>
  <Layout
    nav
    flex
  >
    <Link
      v-for="tab in tabs"
      :key="tab.title"
      v-bind="tab"
      ghost
      min-content
      :class="$style.tab"
    >
      <Layout
        stack
        no-gap
      >
        <span :class="$style.fakeTitle">{{ tab.title }}</span>
        <span :class="$style.realTitle">{{ tab.title }}</span>
        <span
          v-if="tab.badge"
          :class="$style.badge"
        >
          {{ tab.badge }}
        </span>
      </Layout>
    </Link>
  </Layout>
</template>

<style module>
    .fakeTitle {
        font-size: 16px;
        font-weight: 900;
        opacity: 0;
        pointer-events: none;
        max-height: 0;
        overflow: hidden;
    }
    .realTitle {
        font-size: 16px;
        font-weight: 400;
    }
    .tab {
        --hover-background-color: transparent;
        --exact-active-background-color: transparent;
    }
    .tab:global(.router-link-exact-active) .realTitle {
        font-weight: 900;
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
        color: black;
    }
    :is(.tab:global(.router-link-exact-active), .tab:hover) .realTitle:after {
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

</style>
