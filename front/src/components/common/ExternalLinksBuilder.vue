<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { mapUrlToIcon } from '~/utils/mapUrlToIcon'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Layout from '~/components/ui/Layout.vue'

interface ExternalLink {
  label: string
  url: string
}

interface Props {
  links: ExternalLink[]
  maxLinks?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxLinks: 10
})

const cloneLinks = (value: ExternalLink[]) => value.map(link => ({ ...link }))
const links = ref<ExternalLink[]>(cloneLinks(props.links))

watch(() => props.links, (value) => {
  links.value = cloneLinks(value)
})

const { t } = useI18n()

const addLink = () => {
  links.value.push({
    label: t('components.common.ExternalLinksBuilder.label.newLink', {
      linkNumber: links.value.length + 1
    }),
    url: ''
  })
}

const remove = (index: number) => {
  links.value.splice(index, 1)
}

defineExpose({
  getLinks: () => links.value.filter(link => link.label && link.url)
})
</script>

<template>
  <Layout
    stack
  >
    <Layout flex>
      <label>
        {{ t('components.common.ExternalLinksBuilder.label.externalLinks') }}
      </label>
      <span>
        {{ t('components.common.ExternalLinksBuilder.help.externalLinks') }}
      </span>
    </Layout>

    <Layout
      stack
      gap-16
    >
      <Layout
        v-if="links?.length > 0"
        stack
        gap-16
      >
        <Layout
          v-for="(link, key) in links"
          :key="key"
          flex
          gap-16
        >
          <Input
            v-model="link.label"
            type="text"
            required
            :label="key === 0 ? t('components.common.ExternalLinksBuilder.table.header.label') : undefined"
            :placeholder="t('components.common.ExternalLinksBuilder.placeholder.label')"
          />
          <Input
            v-model="link.url"
            type="url"
            required
            :label="key === 0 ? t('components.common.ExternalLinksBuilder.table.header.url') : undefined"
            :icon="mapUrlToIcon(link.url) ?? undefined"
            :placeholder="t('components.common.ExternalLinksBuilder.placeholder.url')"
          />
          <Button
            icon="bi-x"
            destructive
            icon-width
            :style="key === 0 ? 'margin-top: 8px;' : ''"
            @click="remove(key)"
          />
        </Layout>
      </Layout>

      <Button
        v-if="links?.length < maxLinks"
        primary
        icon="bi-plus"
        @click.stop.prevent="addLink"
      >
        {{ t('components.common.ExternalLinksBuilder.button.add') }}
      </Button>
    </Layout>
  </Layout>
</template>
