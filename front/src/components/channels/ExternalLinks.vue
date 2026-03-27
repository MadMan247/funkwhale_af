<script setup lang="ts">
import { resolveLinkMeta } from '~/utils/mapUrlToIcon'

import Link from '~/components/ui/Link.vue'
import Layout from '~/components/ui/Layout.vue'

interface ExternalLink {
  label: string
  url: string
}

interface Props {
  links: ExternalLink[]
}

defineProps<Props>()
</script>

<template>
  <Layout
    v-if="links && links.length > 0"
    flex
    gap-12
  >
    <template
      v-for="(link, key) in links"
      :key="key"
    >
      <Link
        v-for="meta in [resolveLinkMeta(link.url)]"
        :key="meta.iconData as any"
        :to="link.url"
        thin-font
        style="flex: 0 0 auto;"
      >
        <i
          v-if="typeof meta.iconData === 'string'"
          :class="['bi', meta.iconData]"
          :style="{ marginRight: '4px', color: meta.color }"
        />
        <img
          v-else-if="meta.svgDataUrl"
          :src="meta.svgDataUrl"
          :style="{
            width: '1.2rem',
            height: '1.2rem',
            marginRight: '4px',
            display: 'inline-block',
            verticalAlign: 'text-bottom',
            position: 'relative',
            top: '0.1em'
          }"
          :alt="link.label"
        >
        <span>{{ link.label }}</span>
      </Link>
    </template>
  </Layout>
</template>
