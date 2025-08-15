<script setup lang="ts">
import { truncate } from '~/utils/filters'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import DangerousButton from '~/components/common/DangerousButton.vue'
import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import HumanDate from '~/components/common/HumanDate.vue'
import Link from '~/components/ui/Link.vue'
import Heading from '~/components/ui/Heading.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Loader from '~/components/ui/Loader.vue'

import useErrorHandler from '~/composables/useErrorHandler'

interface Props {
  id: number
}

const { t } = useI18n()

const props = defineProps<Props>()

const store = useStore()
const router = useRouter()

const isLoading = ref(false)
const object = ref()
const open = ref(false)

const fetchData = async () => {
  isLoading.value = true

  try {
    const response = await axios.get(`manage/tags/${props.id}/`)
    object.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

fetchData()

const remove = async () => {
  isLoading.value = true

  try {
    await axios.delete(`manage/tags/${props.id}/`)
    router.push({ name: 'manage.library.tags' })
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

const getQuery = (field: string, value: string) => `${field}:"${value}"`
</script>

<template>
  <Loader v-if="isLoading" />
  <Header
    v-if="object"
    v-title="object?.name"
    :h1="'# ' + truncate(object?.name)"
    page-heading
  >
    <Layout
      flex
      class="header-buttons"
    >
      <Link
        solid
        primary
        low-height
        icon="bi-info-circle"
        :to="{ name: 'library.tags.detail', params: { id: object?.name } }"
      >
        {{ t('views.admin.library.TagDetail.link.localProfile') }}
      </Link>
      <dangerous-button
        :is-loading="isLoading"
        :action="remove"
        icon="bi-trash"
        low-height
        :title="t('views.admin.library.TagDetail.modal.delete.header')"
      >
        {{ t('views.admin.library.TagDetail.button.delete') }}
        <template #content>
          {{ t('views.admin.library.TagDetail.modal.delete.content.warning') }}
        </template>
        <template #confirm>
          {{ t('views.admin.library.TagDetail.button.delete') }}
        </template>
      </dangerous-button>
      <Spacer grow />
      <Popover v-model="open">
        <template #default="{ toggleOpen }">
          <OptionsButton
            :title="t('views.admin.library.TagDetail.button.more')"
            is-square-small
            @click="toggleOpen()"
          />
        </template>

        <template #items>
          <PopoverItem
            v-if="store.state.auth.profile?.is_superuser"
            :to="store.getters['instance/absoluteUrl'](`/api/admin/tags/tag/${object?.id}`)"
            icon="bi-wrench"
            target="_blank"
          >
            {{ t('views.admin.library.TagDetail.link.django') }}
          </PopoverItem>
        </template>
      </Popover>
    </Layout>
  </Header>

  <Layout
    flex
    gap-64
  >
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.TagDetail.header.tagData')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TagDetail.table.tag.name') }}
        </span>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.name }}</span>
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.TagDetail.header.activity')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <span class="label">
          {{ t('views.admin.library.TagDetail.table.activity.firstSeen') }}
        </span>
        <Spacer
          h
          grow
        />
        <human-date :date="object?.creation_date" />
      </Layout>
    </Layout>
    <Layout
      stack
      style="flex: 1; gap: 0;"
    >
      <Heading
        :h3="t('views.admin.library.TagDetail.header.audioContent')"
        class="category"
      />
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.artists', query: { q: getQuery('tag', object?.name) } }"
        >
          {{ t('views.admin.library.TagDetail.link.artists') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.artists_count }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.albums', query: { q: getQuery('tag', object?.name) } }"
        >
          {{ t('views.admin.library.TagDetail.link.albums') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.albums_count }}</span>
      </Layout>
      <Layout
        flex
        class="details"
      >
        <Link
          class="label"
          :to="{ name: 'manage.library.tracks', query: { q: getQuery('tag', object?.name) } }"
        >
          {{ t('views.admin.library.TagDetail.link.tracks') }}
        </Link>
        <Spacer
          h
          grow
        />
        <span class="value">{{ object?.tracks_count }}</span>
      </Layout>
    </Layout>
  </Layout>
</template>

<style scoped lang="scss">
@import '~/style/funkwhale.scss';

h3.category {
  margin-bottom: 16px;
}

.details {
  padding: 0 16px;
  height: 72px;
  align-items: center;
  border-top: 1px solid;
  min-width: 280px;

  @include light-theme {
    border-color: var(--fw-gray-300);
  }

  @include dark-theme {
    border-color: var(--fw-gray-800);
  }

  .label {
    font-weight: 800;

    @include light-theme {
      color: var(--fw-gray-600);
    }

    @include dark-theme {
      color: var(--fw-gray-500);
    }
  }

  a.label,
  a.value {
    text-decoration: underline;
  }

  &:last-child {
    border-bottom: 1px solid;
  }
}
</style>
