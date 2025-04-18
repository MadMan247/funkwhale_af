<script setup lang="ts">
import type { Library } from '~/types'

import { onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router'
import { computed, ref, watch, watchEffect } from 'vue'
import { humanSize } from '~/utils/filters'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import LibraryFollowButton from '~/components/audio/LibraryFollowButton.vue'
import RadioButton from '~/components/radios/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Loader from '~/components/ui/Loader.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Header from '~/components/ui/Header.vue'
import Nav from '~/components/ui/Nav.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useReport from '~/composables/moderation/useReport'

interface Props {
  id: number
}

const props = defineProps<Props>()

const { report, getReportableObjects } = useReport()
const store = useStore()

const object = ref<Library | null>(null)

const isOwner = computed(() => store.state.auth.authenticated && object.value?.actor.full_username === store.state.auth.fullUsername)
const isPlayable = computed(() => (object.value?.uploads_count ?? 0) > 0 && (
  isOwner.value
    || object.value?.privacy_level === 'everyone'
    || (object.value?.privacy_level === 'instance' && store.state.auth.authenticated && object.value.actor.domain === store.getters['instance/domain'])
    || (store.getters['libraries/follow'](object.value?.uuid) || {}).approved === true
))

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.library.LibraryBase.title'),
  visibility: {
    me: t('views.library.LibraryBase.label.private'),
    instance: t('views.library.LibraryBase.label.instance'),
    everyone: t('views.library.LibraryBase.label.public')
  },
  tooltips: {
    me: t('views.library.LibraryBase.tooltip.private'),
    instance: t('views.library.LibraryBase.tooltip.instance'),
    everyone: t('views.library.LibraryBase.tooltip.public')
  }
}))

onBeforeRouteUpdate((to) => {
  to.meta.preserveScrollPosition = true
})

const isLoading = ref(false)
const fetchData = async () => {
  isLoading.value = true
  try {
    const response = await axios.get(`libraries/${props.id}`)
    object.value = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

watch(() => props.id, fetchData, { immediate: true })

const route = useRoute()
const router = useRouter()
watchEffect(() => {
  if (!store.state.auth.authenticated && object.value && store.getters['instance/domain'] !== object.value.actor.domain) {
    router.push({ name: 'login', query: { next: route.fullPath } })
  }
})

const updateUploads = (count: number) => {
  object.value = object.value
    ? { ...object.value, uploads_count: object.value.uploads_count + count }
    : null
}

const tabs = ref([{
  title: t('views.library.LibraryBase.link.artists'),
  to: { name: 'library.detail' }
}, {
  title: t('views.library.LibraryBase.link.albums'),
  to: { name: 'library.detail.albums' }
}, {
  title: t('views.library.LibraryBase.link.tracks'),
  to: { name: 'library.detail.tracks' }
}
])
</script>

<template>
  <Layout
    v-title="labels.title"
    stack
    main
  >
    <Loader v-if="isLoading" />
    <Header
      page-heading
      :h1="object?.name"
    >
      <template #action>
        <Popover>
          <template #default="{ toggleOpen }">
            <OptionsButton
              @click="toggleOpen"
            />
          </template>

          <template #items>
            <PopoverItem
              v-if="object?.actor.domain != store.getters['instance/domain']"
              :to="object?.fid"
              target="_blank"
              icon="bi-box-arrow-up-right"
            >
              {{ t('views.library.LibraryBase.link.domain', {domain: object?.actor.domain}) }}
            </PopoverItem>
            <PopoverItem
              v-for="obj in getReportableObjects({library: object})"
              :key="obj.target.type + obj.target.id"
              icon="bi-share"
              @click.stop.prevent="report(obj)"
            >
              {{ obj.label }}
            </PopoverItem>

            <hr>

            <PopoverItem
              v-if="store.state.auth.availablePermissions['moderation']"
              icon="bi-wrench"
              :to="{name: 'manage.library.libraries.detail', params: {id: object?.uuid}}"
            >
              {{ t('views.library.LibraryBase.link.moderation') }}
            </PopoverItem>
          </template>
        </Popover>
      </template>
    </Header>
    <div
      class="sub header ellipsis"
      :title="object?.actor.full_username"
    >
      <actor-link
        :avatar="false"
        :actor="object?.actor"
        :truncate-length="0"
      >
        {{ t('views.library.LibraryBase.link.owner', {username: object?.actor.full_username}) }}
      </actor-link>
    </div>
    <Layout flex>
      <span
        v-if="object?.privacy_level === 'me'"
        :title="labels.tooltips.me"
      >
        <i class="bi bi-lock" />
        {{ labels.visibility.me }}
      </span>
      <span
        v-else-if="object?.privacy_level === 'instance'"
        :title="labels.tooltips.instance"
      >
        <i class="bi bi-lock-open" />
        {{ labels.visibility.instance }}
      </span>
      <span
        v-else-if="object?.privacy_level === 'everyone'"
        :title="labels.tooltips.everyone"
        class="bi bi-dot"
      >
        <i class="bi bi-globe" />
        {{ labels.visibility.everyone }}
      </span>
      <span
        v-if="object"
        class="middledot icon"
      >
        <i class="bi bi-music-note-list" />
        {{ t('views.library.LibraryBase.meta.tracks', object.uploads_count) }}
      </span>
      <span v-if="object && 'size' in object && object.size && typeof object.size === 'number'">
        <i class="bi bi-database-fill" />
        {{ humanSize(object.size as number) }}
      </span>
    </Layout>

    <Layout
      flex
      class="header-buttons"
    >
      <radio-button
        :disabled="!isPlayable || null"
        type="library"
        :object-id="object?.uuid"
      />
      <div
        v-if="!isOwner"
      >
        <library-follow-button
          v-if="store.state.auth.authenticated && object"
          :library="object"
        />
      </div>
    </Layout>

    <!-- TODO: Add `description` field to library -->
    <!-- @vue-ignore -->
    <rendered-description
      v-if="object && 'description' in object"
      :content="{ html: object.description }"
      :update-url="`channels/${object.uuid}/`"
      :can-update="false"
    />
    <Layout form>
      <div class="field">
        <copy-input
          :value="object?.fid"
          :label="t('views.library.LibraryBase.label.sharingLink')"
        />
        <p>
          {{ t('views.library.LibraryBase.description.sharingLink') }}
        </p>
      </div>
    </Layout>
    <Nav v-model="tabs" />

    <router-view
      :is-owner="isOwner"
      :object="object"
      @updated="fetchData"
      @uploads-finished="updateUploads"
    />
  </Layout>
</template>
