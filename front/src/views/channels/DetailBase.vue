<script setup lang="ts">
import type { Channel } from '~/types'

import { onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router'
import { computed, ref, reactive, watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useModal } from '~/ui/composables/useModal.ts'

import axios from 'axios'

import useErrorHandler from '~/composables/useErrorHandler'
import useReport from '~/composables/moderation/useReport'

import DangerousButton from '~/components/common/DangerousButton.vue'
import SubscribeButton from '~/components/channels/SubscribeButton.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'
import EmbedWizard from '~/components/audio/EmbedWizard.vue'
import HumanDuration from '~/components/common/HumanDuration.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import TagsList from '~/components/tags/List.vue'
import RadioButton from '~/components/radios/Button.vue'

import Loader from '~/components/ui/Loader.vue'
import Layout from '~/components/ui/Layout.vue'
import Header from '~/components/ui/Header.vue'
import Button from '~/components/ui/Button.vue'
import Link from '~/components/ui/Link.vue'
import Nav from '~/components/ui/Nav.vue'
import OptionsButton from '~/components/ui/button/Options.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Modal from '~/components/ui/Modal.vue'

interface Events {
  (e: 'deleted'): void
}

interface Props {
  id: number
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()
const { report, getReportableObjects } = useReport()
const store = useStore()

const object = ref<Channel | null>(null)
const editForm = ref()
const totalTracks = ref(0)

const edit = reactive({
  submittable: false,
  loading: false
})

const showEmbedModal = ref(false)
const showEditModal = ref(false)
const showSubscribeModal = ref(false)

const isOwner = computed(() => store.state.auth.authenticated && object.value?.attributed_to.full_username === store.state.auth.fullUsername)
const isPlayable = computed(() => totalTracks.value > 0)
const externalDomain = computed(() => {
  const parser = document.createElement('a')
  parser.href = object.value?.url ?? object.value?.rss_url ?? ''
  return parser.hostname
})

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.channels.DetailBase.title')
}))

onBeforeRouteUpdate((to) => {
  to.meta.preserveScrollPosition = true
})

const router = useRouter()
const isLoading = ref(false)
const fetchData = async () => {
  showEditModal.value = false
  edit.loading = false
  isLoading.value = true

  try {
    const response = await axios.get(`channels/${props.id}`, { params: { refresh: 'true' } })
    object.value = response.data
    totalTracks.value = response.data.artist.tracks_count

    if (props.id === response.data.uuid && response.data.actor) {
      // replace with the pretty channel url if possible
      const actor = response.data.actor
      if (actor.is_local) {
        await router.replace({ name: 'channels.detail', params: { id: actor.preferred_username } })
      } else {
        await router.replace({ name: 'channels.detail', params: { id: actor.full_username } })
      }
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

watch(() => props.id, fetchData, { immediate: true })

const uuid = computed(() => store.state?.channels.latestPublication?.channel.uuid)

watch([uuid, object], ([uuid, object], [lastUuid, lastObject]) => {
  if (object?.uuid && object.uuid === lastObject?.uuid) return

  if (uuid && uuid === object?.uuid) {
    fetchData()
  }
})

const route = useRoute()
watchEffect(() => {
  if (!object.value) {
    store.state.channels.uploadModalConfig.channel = null
    return
  } else {
    store.state.channels.uploadModalConfig.channel = object.value
  }

  if (!store.state.auth.authenticated && store.getters['instance/domain'] !== object.value.actor.domain) {
    router.push({ name: 'login', query: { next: route.fullPath } })
  }
})

const remove = async () => {
  isLoading.value = true
  try {
    await axios.delete(`channels/${object.value?.uuid}`)
    emit('deleted')
    return router.push({ name: 'profile.overview', params: { username: store.state.auth.username } })
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const updateSubscriptionCount = (delta: number) => {
  if (object.value) {
    // TODO: Store a modified copy in the cache or on the db instead of mutating the object in-memory.
    // #2438
    // @ts-expect-error Property 'subscriptions_count' is readonly on type 'Channel'
    object.value.subscriptions_count -= delta
  }
}

const tabs = ref([
  {
    title: t('views.channels.DetailBase.link.channelOverview'),
    to: {name: 'channels.detail', params: { id: props.id }}

  },
  {
    title: t('views.channels.DetailBase.link.channelEpisodes'),
    to: {name: 'channels.detail.episodes', params: { id: props.id }}
  }
])
</script>

<template>
  <Layout
    v-title="labels.title"
    stack
    no-gap
    main
  >
    <Loader v-if="isLoading" />
    <Header
      v-if="object && !isLoading"
      v-title="object.artist?.name"
      :h1="object.artist?.name"
      page-heading
    >
      <template #image>
        <img
          v-if="object.artist?.cover"
          alt=""
          :class="['huge', object.artist?.content_category === 'podcast' ? 'podcast-image' : 'channel-image']"
          :src="store.getters['instance/absoluteUrl'](object.artist.cover.urls.large_square_crop)"
        >
        <i
          v-else
          class="bi bi-person-circle"
          style="font-size: 300px; margin-top: -32px;"
        />
      </template>
      <Layout
        stack
        class="meta"
        style="gap: 8px;"
      >
        <Layout
          flex
          no-gap
        >
          <template v-if="totalTracks > 0">
            <span
              v-if="object.artist?.content_category === 'podcast'"
            >
              {{ t('views.channels.DetailBase.meta.episodes', totalTracks) }}
            </span>
            <span
              v-else
            >
              {{ t('views.channels.DetailBase.meta.tracks', totalTracks) }}
            </span>
            <i class="bi bi-dot" />
          </template>
          {{ t('views.channels.DetailBase.meta.subscribers', object?.subscriptions_count ?? 0) }}
          <i class="bi bi-dot" />
          {{ t('views.channels.DetailBase.meta.listenings', object?.downloads_count ?? 0) }}

          <div v-if="totalTracks > 0">
            <i class="bi bi-dot" />
            <human-duration
              v-if="totalTracks > 0"
              :duration="totalTracks"
            />
          </div>
        </Layout>
        <Layout
          flex
          no-gap
        >
          <template v-if="object.artist?.content_category === 'podcast'">
            <span>
              {{ t('views.channels.DetailBase.header.podcastChannel') }}
            </span>
            <span
              v-if="!object.actor"
            >
              <i class="bi bi-dot" />
              <a
                :href="object.url || object.rss_url"
                rel="noopener noreferrer"
                target="_blank"
              >
                <i class="bi bi-box-arrow-up-right" />
                {{ t('views.channels.DetailBase.link.mirrored', {domain: externalDomain}) }}
              </a>
            </span>
          </template>
          <template v-else>
            <span>
              {{ t('views.channels.DetailBase.header.artistChannel') }}
            </span>
          </template>
          <span v-if="object.actor">
            <i class="bi bi-dot" />
            {{ t('views.library.LibraryBase.link.owner') }}
          </span>
          <Spacer
            h
            :size="8"
          />
          <ActorLink
            v-if="object.actor"
            discrete
            :avatar="true"
            :actor="object.attributed_to"
            :display-name="true"
          />
        </Layout>
      </Layout>
      <rendered-description
        :content="object.artist?.description"
        :update-url="`channels/${object.uuid}/`"
        :can-update="false"
        @updated="object = $event"
      />
      <Layout
        flex
        class="header-buttons"
      >
        <!-- TODO: Deeplink to channel upload with the channel selected -->
        <Link
          v-if="isOwner"
          solid
          primary
          low-height
          icon="bi-upload"
          channel="object"
          filter="object.artist?.content_category === 'podcast' ? 'podcast' : 'music'"
          :to="useModal('upload').to"
        >
          {{ t('views.channels.DetailBase.button.upload') }}
        </Link>
        <PlayButton
          :is-playable="isPlayable"
          split
          low-height
          class="vibrant"
          :artist="object.artist"
        >
          {{ t('views.channels.DetailBase.button.play') }}
        </PlayButton>
        <RadioButton
          type="artist"
          :object-id="object.artist.id"
          low-height
        />

        <Popover>
          <template #default="{ toggleOpen }">
            <OptionsButton
              is-square-small
              @click="toggleOpen"
            />
          </template>
          <template #items>
            <PopoverItem
              v-if="totalTracks > 0"
              icon="bi-code-slash"
              @click.prevent="showEmbedModal = !showEmbedModal"
            >
              {{ t('views.channels.DetailBase.button.embed') }}
            </PopoverItem>
            <PopoverItem
              v-if="object.actor && object.actor.domain != store.getters['instance/domain']"
              :href="object.url"
              target="_blank"
              icon="bi-box-arrow-up-right"
            >
              {{ t('views.channels.DetailBase.link.domainView', {domain: object.actor.domain}) }}
            </PopoverItem>
            <hr>
            <PopoverItem
              v-for="obj in getReportableObjects({account: object.attributed_to, channel: object})"
              :key="obj.target.type + obj.target.id"
              icon="bi-share"
              @click.stop.prevent="report(obj)"
            >
              {{ obj.label }}
            </PopoverItem>

            <template v-if="isOwner">
              <hr>
              <PopoverItem
                icon="bi-pencil"
                @click.stop.prevent="showEditModal = true"
              >
                {{ t('views.channels.DetailBase.button.edit') }}
              </PopoverItem>
              <dangerous-button
                v-if="object"
                popover-item
                :title="t('views.channels.DetailBase.button.confirm')"
                :is-loading="isLoading"
                icon="bi-trash"
                @confirm="remove()"
              >
                {{ t('views.channels.DetailBase.button.confirm') }}
                <template #modal-content>
                  {{ t('views.channels.DetailBase.modal.delete.content.warning') }}
                </template>
                <template #modal-confirm>
                  <p>
                    {{ t('views.channels.DetailBase.button.confirm') }}
                  </p>
                </template>
              </dangerous-button>
            </template>
            <template v-if="store.state.auth.availablePermissions['library']">
              <hr>
              <PopoverItem
                :to="{ name: 'manage.channels.detail', params: { id: object.uuid } }"
                icon="bi-wrench"
              >
                {{ t('views.channels.DetailBase.link.moderation') }}
              </PopoverItem>
            </template>
          </template>
        </Popover>
        <Spacer
          h
          grow
        />
        <subscribe-button
          v-if="store.state.auth.authenticated && object?.attributed_to.full_username !== store.state.auth.fullUsername"
          low-height
          :channel="object"
          @subscribed="updateSubscriptionCount(1)"
          @unsubscribed="updateSubscriptionCount(-1)"
        />

        <Modal
          v-if="totalTracks > 0"
          v-model="showEmbedModal"
          :title="t('views.channels.DetailBase.modal.embed.header')"
          :cancel="t('views.channels.DetailBase.button.cancel')"
        >
          <div class="scrolling content">
            <div class="description">
              <embed-wizard
                :id="object.artist!.id"
                type="artist"
              />
            </div>
          </div>
          <template #actions>
            <button class="ui basic deny button">
              {{ t('views.channels.DetailBase.button.cancel') }}
            </button>
          </template>
        </Modal>
        <Modal
          v-if="isOwner"
          v-model="showEditModal"
          :title="
            object.artist?.content_category === 'podcast'
              ? t('views.channels.DetailBase.header.podcastChannel')
              : t('views.channels.DetailBase.header.artistChannel')
          "
        >
          <div class="scrolling content">
            <channel-form
              ref="editForm"
              :object="object"
              @loading="edit.loading = $event"
              @submittable="edit.submittable = $event"
              @updated="fetchData"
            />
            <div class="ui hidden divider" />
          </div>
          <template #actions>
            <Button
              primary
              autofocus
              low-height
              :is-loading="edit.loading"
              :disabled="!edit.submittable"
              @click.stop="editForm?.submit"
            >
              {{ t('views.channels.DetailBase.button.updateChannel') }}
            </Button>
          </template>
        </Modal>
        <Button
          secondary
          icon="bi-rss"
          square-small
          @click.stop.prevent="showSubscribeModal = true"
        />
        <Modal
          v-model="showSubscribeModal"
          :title="t('views.channels.DetailBase.modal.subscribe.header')"
          class="tiny"
          :cancel="t('views.channels.DetailBase.button.cancel')"
        >
          <div class="scrollable content">
            <Layout class="description">
              <template v-if="object.rss_url">
                <h3>
                  <i class="feed icon" />
                  {{ t('views.channels.DetailBase.modal.subscribe.rss.header') }}
                </h3>
                <copy-input
                  :value="object.rss_url"
                  :label="t('views.channels.DetailBase.modal.subscribe.rss.content.help')"
                />
              </template>
              <template v-if="object.actor">
                <h3>
                  <i class="bell icon" />
                  {{ t('views.channels.DetailBase.modal.subscribe.fediverse.header') }}
                </h3>
                <copy-input
                  id="copy-tag"
                  :value="`@${object.actor.full_username}`"
                  :label="t('views.channels.DetailBase.modal.subscribe.fediverse.content.help')"
                />
              </template>
            </Layout>
          </div>
        </Modal>
      </Layout>
    </Header>
    <hr>
    <TagsList
      v-if="object?.artist?.tags && object?.artist?.tags.length > 0"
      :tags="object?.artist.tags"
      :limit="5"
      :show-more="true"
    />
    <Nav v-model="tabs" />

    <router-view
      v-if="object"
      :object="object"
      @tracks-loaded="totalTracks = $event"
    />
  </Layout>
</template>

<style scoped lang="scss">
  .channel-image {
    border-radius: 50%;
  }
  .huge {
    width: 200px;
    height: 200px;
  }
  .meta {
    font-size: 15px;
    @include light-theme {
      color: var(--fw-gray-700);
    }
    @include dark-theme {
      color: var(--fw-gray-500);
    }
  }
</style>
