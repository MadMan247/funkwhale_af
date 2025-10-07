<script setup lang="ts">
import type { Notification, LibraryFollow } from '~/types'
import type { components } from '~/generated/types'
import type { RouteLocationRaw } from 'vue-router'

import { computed, ref, watchEffect, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import Alert from '~/components/ui/Alert.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Props {
  initialItem: Notification
}

const props = defineProps<Props>()

const { t } = useI18n()
const store = useStore()

const labels = computed(() => ({
  markRead: t('components.notifications.NotificationRow.button.markRead'),
  markUnread: t('components.notifications.NotificationRow.button.markUnread')
}))

const item = ref(props.initialItem)
watchEffect(() => (item.value = props.initialItem))

const username = computed(() => props.initialItem.activity.actor.preferred_username)
const notificationData = computed(() => {
  const activity = props.initialItem.activity

  if (activity.type === 'Follow') {
    if (activity.type === 'Follow' && activity.object?.type === 'music.Library') {
      const libraryFollow = activity.related_object as LibraryFollow

      const detailUrl = { name: 'library.detail.edit', params: { id: activity.object.uuid } }

      if (activity.related_object?.approved === null) {
        // to do : dirty hack
      let labelPendingFollow = ""
      if (typeof activity.object?.name === 'string' && activity.object.name.startsWith('playlist_')) {
          labelPendingFollow = t('components.notifications.NotificationRow.message.playlistPendingFollow', { username: username.value, library: activity.object.name.slice("playlist_".length) })
        }
        else {
          labelPendingFollow = t('components.notifications.NotificationRow.message.libraryPendingFollow', { username: username.value, library: activity.object.name })

        }
        return {
          detailUrl,
          message: labelPendingFollow,
          acceptFollow: {
            buttonClass: 'success',
            icon: 'check',
            label: t('components.notifications.NotificationRow.button.approve'),
            handler: () => approveLibraryFollow(libraryFollow)
          },
          rejectFollow: {
            buttonClass: 'danger',
            icon: 'x',
            label: t('components.notifications.NotificationRow.button.reject'),
            handler: () => rejectLibraryFollow(libraryFollow)
          }
        }
      } else if (activity.related_object?.approved) {
        let labelFollow = ""
        if (typeof activity.object?.name === 'string' && activity.object.name.startsWith('playlist_')) {
          labelFollow = t('components.notifications.NotificationRow.message.playlistFollow', { username: username.value, library: activity.object.name.slice("playlist_".length) })
        }
        else {
          labelFollow = t('components.notifications.NotificationRow.message.libraryFollow', { username: username.value, library: activity.object.name })

        }
        return {
          detailUrl,
          message: labelFollow
        }
      }
      let labelReject = ""
        if (typeof activity.object?.name === 'string' && activity.object.name.startsWith('playlist_')) {
          labelReject = t('components.notifications.NotificationRow.message.playlistlReject', { username: username.value, library: activity.object.name.slice("playlist_".length) })
        }
        else {
          labelReject = t('components.notifications.NotificationRow.message.libraryReject', { username: username.value, library: activity.object.name })

        }
      return {
        detailUrl,
        message: labelReject
      }
    }
    if (activity.object && activity.object.type === 'federation.Actor') {
      // TODO: Correctly type `activity` instead of coercing the field:
      const userFollow = activity.related_object as components["schemas"]["Follow"]
      const detailUrl = { name: 'profile.full', params: { username: activity.actor.preferred_username, domain: activity.actor.domain } }

      if (activity.related_object?.approved === null) {
        return {
          detailUrl,
          message: t('components.notifications.NotificationRow.message.userPendingFollow', { username: username.value,
            // TODO: This is just wrong. Start with fixing the types upstream.
            // @ts-expect-error `activity.object needs to have a type. Where is it declared?
            user: activity.object.target?.full_username }),
          acceptFollow: {
            buttonClass: 'success',
            icon: 'bi-check',
            label: t('components.notifications.NotificationRow.button.approve'),
            handler: () => approveUserFollow(userFollow)
          },
          rejectFollow: {
            buttonClass: 'danger',
            icon: 'bi-x',
            label: t('components.notifications.NotificationRow.button.reject'),
            handler: () => rejectUserFollow(userFollow)
          }
        }
      } else if (activity.related_object?.approved) {
        return {
          detailUrl,
          message: t('components.notifications.NotificationRow.message.userFollow', { username: username.value, user: activity.actor.full_username })
        }
      }

      return {
        detailUrl,
        message: t('components.notifications.NotificationRow.message.userReject', { username: username.value, user: activity.actor.full_username })
      }
    }
  }

  if (activity.type === 'Accept') {
    if (activity.object?.type === 'federation.LibraryFollow') {
      return {
        detailUrl: { name: 'content.remote.index' },
        message: t('components.notifications.NotificationRow.message.libraryAcceptFollow', { username: username.value, library: activity.related_object.name })
      }
    }
    if (activity.object?.type === 'federation.Actor') {
      return {
        detailUrl: { name: 'content.remote.index' },
        message: t('components.notifications.NotificationRow.message.userAcceptFollow', { username: username.value, user: activity.actor.full_username })
      }
    }
  }

  return {}
})

const read = ref(false)
watch(read, async () => {
  await axios.patch(`federation/inbox/${item.value.id}/`, { is_read: read.value })

  item.value.is_read = read.value
  store.commit('ui/incrementNotifications', { type: 'inbox', count: read.value ? -1 : 1 })
})

const handleAction = (handler?: () => void) => {
  // call handler then mark notification as read
  handler?.()
  read.value = true
}

const approveLibraryFollow = async (follow: LibraryFollow) => {
  await axios.post(`federation/follows/library/${follow.uuid}/accept/`)
  // TODO: This is not how Axios works. You have to send a request with
  // the correct type as a parameter.
  // @ts-expect-error Post this with the axios payload: { ...follow, approved: true}
  follow.approved = true
  item.value.is_read = true
}

const rejectLibraryFollow = async (follow: LibraryFollow) => {
  await axios.post(`federation/follows/library/${follow.uuid}/reject/`)
  // TODO: This is not how Axios works. You have to send a request with
  // the correct type as a parameter.
  // @ts-expect-error Post this with the axios payload: { ...follow, approved: false}
  follow.approved = false
  item.value.is_read = true
}

const approveUserFollow = async (follow: components["schemas"]["Follow"]) => {
  await axios.post(`federation/follows/user/${follow.uuid}/accept/`)
  // TODO: This is not how Axios works. You have to send a request with
  // the correct type as a parameter.
  // @ts-expect-error Post this with the axios payload: { ...follow, approved: true}
  follow.approved = true
  item.value.is_read = true
}

const rejectUserFollow = async (follow: components["schemas"]["Follow"]) => {
  await axios.post(`federation/follows/user/${follow.uuid}/reject/`)

  // TODO: This is not how Axios works. You have to send a request with
  // the correct type as a parameter.
  // @ts-expect-error Post this with the axios payload: { ...follow, approved: false}
  follow.approved = false
  item.value.is_read = true
}
</script>

<template>
  <Alert
    :class="[{'disabled-row': item.is_read}]"
    :green="item.is_read"
    :yellow="!item.is_read"
  >
    <Layout
      flex
      gap-8
    >
      <actor-link
        class="user"
        :actor="item.activity.actor"
      />
      <!-- TODO: Make sure `notificationData.detailUrl` has a type that satisfies `RouteLocationRaw` -->
      <!-- @vue-ignore -->
      <router-link
        v-if="notificationData.detailUrl"
        v-slot="{ navigate }"
        custom
        :to="notificationData.detailUrl as RouteLocationRaw"
      >
        <sanitized-html
          tag="span"
          class="link"
          :html="notificationData.message"
          @click="navigate()"
          @keypress.enter="navigate()"
        />
      </router-link>
      <sanitized-html
        v-else
        :html="notificationData.message"
      />
      <Spacer grow />
      <human-date :date="item.activity.creation_date" />
      <Button
        v-if="item.is_read"
        href=""
        :aria-label="labels.markUnread"
        class="discrete link"
        :title="labels.markUnread"
        icon="bi-arrow-clockwise"
        yellow
        square-small
        @click.prevent="read = false"
      />
      <Button
        v-else
        href=""
        :aria-label="labels.markRead"
        class="discrete link"
        :title="labels.markRead"
        icon="bi-check"
        green
        square-small
        @click.prevent="read = true"
      />
    </Layout>
    <Spacer />
    <template
      v-if="notificationData.acceptFollow"
      #actions
    >
&nbsp;
      <Button
        :class="['ui', 'basic', 'tiny', notificationData.acceptFollow.buttonClass || '', 'button']"
        :icon="notificationData.acceptFollow.icon"
        green
        @click="handleAction(notificationData.acceptFollow?.handler)"
      >
        {{ notificationData.acceptFollow.label }}
      </Button>
      <Button
        :class="['ui', 'basic', 'tiny', notificationData.rejectFollow.buttonClass || '', 'button']"
        :icon="notificationData.rejectFollow.icon"
        red
        @click="handleAction(notificationData.rejectFollow?.handler)"
      >
        {{ notificationData.rejectFollow.label }}
      </Button>
    </template>
  </Alert>
</template>
