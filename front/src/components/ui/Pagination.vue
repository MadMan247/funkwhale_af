<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { ref, computed, watch } from 'vue'
import { isMobileView } from '~/composables/screen'

import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Spacer from '~/components/ui/Spacer.vue'

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

/* Render only pages nearby if >5 pages:
- If near the end, show 1, ..., end-4, end-3, end-2, end-1, end
- If smaller than -4 and larger than 4, show 1, ..., current-1, current, current+1, ..., end
- If near beginning, show 1, 2, 3, 4, 5, ..., 12
*/
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


<!-- REDESIGN, without custom CSS -->



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
          :square-small="isSmall"
          :disabled="page <= 1"
          :aria-label="t('vui.aria.pagination.gotoPrevious')"
          secondary
          ghost
          icon="bi-chevron-left"
          class="visually-hidden-when-small"
          @click="page -= 1"
        >
          <span v-if="!isSmall">{{ t('vui.pagination.previous') }}</span>
        </Button>
      </li>

      <Spacer
        no-size
        grow
      />

      <template
        v-for="(i, index) in (renderPages)"
        :key="i"
      >
        <li>
          <Button
            v-if="i <= pages && i > 0 && pages > 2"
            square-small
            :aria-label="page !== i ? t('vui.aria.pagination.gotoPage', i) : t('vui.aria.pagination.currentPage', page)"
            :secondary="page !== i"
            :aria-pressed="page === i"
            circular
            ghost
            @click="page = i"
          >
            {{ i }}
          </Button>
        </li>
        <li
          v-if="i + 1 < renderPages[index + 1]"
          style="user-select: none;"
        >
          {{ t('vui.pagination.ellipsis') }}
        </li>
      </template>

      <Spacer
        no-size
        grow
      />

      <li>
        <Button
          low-height
          min-content
          :square-small="isSmall"
          :disabled="page >= pages"
          :aria-label="t('vui.aria.pagination.gotoNext')"
          secondary
          ghost
          icon="right bi-chevron-right"
          class="visually-hidden-when-small"
          @click="page += 1"
        >
          <span v-if="!isSmall">{{ t('vui.pagination.next') }}</span>
        </Button>
      </li>
    </ul>
    <!-- \d{1,100} -->
    <Spacer size-8 />
    <label style="transform: translateY(-7px);">
      <Input
        v-model.number="goTo"
        :placeholder="t('vui.pagination.enterPageNumber')"
        low-height
        tiny
        inputmode="numeric"
        pattern="[0-9]*"
        :aria-label="t('vui.aria.pagination.goToPage', { goTo })"
        @click.stop
        @keyup.enter="setPage"
        @blur="setPage"
      />
    </label>
  </nav>
</template>

<style>
.funkwhale.pagination {

    /* People using a screen reader want to be able to use default 'previous page', 'next page' controls*/
    @media screen and (max-width: 671px) {
        flex-wrap: wrap;
        .visually-hidden-when-small:not(:focus):not(:active) {
           	border: 0;
           	clip: rect(0 0 0 0);
           	clip-path: inset(50%);
           	height: 1px;
           	margin: -1px;
           	overflow: hidden;
           	padding: 0;
           	position: absolute;
           	white-space: nowrap;
           	width: 1px;
        }
    }

    height: 34px;
    display: flex;
    justify-content: center;

    &.is-small {
      > .pages {
        width: auto;
      }
      > .goto {
        margin-right: auto;
      }
    }

    > ul.pages {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      list-style: none;
      margin: 0;
      padding: 0;
      gap: 4px;
      margin-bottom: 8px;

      > li {
        margin: 0;
        text-align: center;

        &:not(:first-child):not(:last-child) {
          min-width: 34px;
        }

        &:first-child > .funkwhale.button,
        &:last-child > .funkwhale.button {
          width: 94px;
          text-align: center;
        }
      }
    }
  }
</style>
