<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { ref, computed, watch } from 'vue'
import { isMobileView } from '~/composables/screen'

import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'

const { t } = useI18n()

type NonnegativeInteger<T extends number> =
  `${T}` extends `-${any}` | `${any}.${any}` ? never : T

const { pages } = defineProps<{ pages: NonnegativeInteger<number> }>()

const page = defineModel<number>('page', {
  required: true,
  validator: (value: number) => value > 0
})

const goTo = ref<number | string>('' as const)

const range = (start: number, end: number) => Array.from({ length: end - start + 1 }, (_, i) => i + start)

/* Why? What? */
const renderPages = computed(() => {
  const start = range(2, 5)
  const end = range(pages - 4, pages - 1)

  const pagesArray = [1]

  if (page.value < 5) pagesArray.push(...start)
  if (page.value >= 5 && page.value <= pages - 4) {
    pagesArray.push(page.value - 1)
    pagesArray.push(page.value)
    pagesArray.push(page.value + 1)
  }
  if (page.value > pages - 4) pagesArray.push(...end)
  pagesArray.push(pages)

  return pagesArray.filter((page, index, pages) => pages.indexOf(page) === index)
})

const pagination = ref()
const { width } = useElementSize(pagination)
const isSmall = isMobileView(width)

const setPage = () => {
  if (goTo.value === '') return
  page.value = pageFromInput(goTo.value)
}

watch(goTo, potentiallyWrongValue => {
  goTo.value = typeof potentiallyWrongValue === 'string'
    ? ''
    : pageFromInput(potentiallyWrongValue)
})

const pageFromInput = (input: string | number): number =>
  input === 'NaN'
    ? pageFromInput('')
    : typeof input === 'string'
      ? pageFromInput(parseInt(input))
      : Number.isNaN(input)
        ? 1
        : Math.min(Math.max(1, input), pages)

/* When user changes page, the "GoTo" input should be emptied */
watch(page, (_) => {
  goTo.value = ''
})
</script>

<template>
  <nav
    ref="pagination"
    :aria-label="t('vui.aria.pagination.nav')"
    :class="{ 'is-small': isSmall }"
    class="funkwhale pagination"
    role="navigation"
  >
    <ul class="pages">
      <li>
        <Button
          low-height
          min-content
          :disabled="page <= 1"
          :aria-label="t('vui.aria.pagination.gotoPrevious')"
          secondary
          icon="bi-chevron-left"
          @click="page -= 1"
        >
          <span v-if="!isSmall">{{ t('vui.pagination.previous') }}</span>
        </Button>
      </li>

      <template
        v-for="(i, index) in (isSmall ? [] : renderPages)"
        :key="i"
      >
        <li>
          <Button
            v-if="i <= pages && i > 0 && pages > 3"
            square-small
            :aria-label="page !== i ? t('vui.aria.pagination.gotoPage', i) : t('vui.aria.pagination.currentPage', page)"
            :secondary="page !== i"
            @click="page = i"
          >
            {{ i }}
          </Button>
        </li>
        <li v-if="i + 1 < renderPages[index + 1]">
          {{ (() => '…')() }}
        </li>
      </template>
      <template v-if="isSmall">
        <li>
          <Button
            square-small
            :aria-label="page !== 1 ? t('vui.aria.pagination.gotoPage', page) : t('vui.aria.pagination.currentPage', page)"
            :secondary="page !== 1"
            @click="page = 1"
          >
            {{ (() => '1')() }}
          </Button>
        </li>
        <li v-if="page === 1 || page === pages">
          {{ (() => '…')() }}
        </li>
        <li v-else>
          <Button
            square-small
            :aria-label="t('vui.aria.pagination.currentPage', page)"
            aria-current="true"
          >
            {{ page }}
          </Button>
        </li>
        <li>
          <Button
            square-small
            :aria-label="page !== pages ? t('vui.aria.pagination.gotoPage', page) : t('vui.aria.pagination.currentPage', page)"
            :secondary="page !== pages"
            @click="page = pages"
          >
            {{ pages }}
          </Button>
        </li>
      </template>

      <li>
        <Button
          low-height
          min-content
          :disabled="page >= pages"
          :aria-label="t('vui.aria.pagination.gotoNext')"
          secondary
          icon="right bi-chevron-right"
          @click="page += 1"
        >
          <span v-if="!isSmall">{{ t('vui.pagination.next') }}</span>
        </Button>
      </li>
    </ul>
    <!-- \d{1,100} -->
    <div class="goto">
      {{ t('vui.go-to') }}
      <Input
        v-model.number="goTo"
        :placeholder="page?.toString()"
        inputmode="numeric"
        pattern="[0-9]*"
        @click.stop
        @keyup.enter="setPage"
      />
    </div>
  </nav>
</template>

<style lang="scss">
@import './pagination.scss'
</style>
