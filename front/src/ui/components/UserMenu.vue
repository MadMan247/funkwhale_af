<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useStore } from '~/store'
import { useRoute } from 'vue-router'

import useThemeList from '~/composables/useThemeList'
import useTheme from '~/composables/useTheme'

import { useModal } from '~/ui/composables/useModal.ts'

import Button from '~/components/ui/Button.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import PopoverSubmenu from '~/components/ui/popover/PopoverSubmenu.vue'
import Spacer from '~/components/ui/Spacer.vue'

const route = useRoute()
const store = useStore()

const { t } = useI18n()

const themes = useThemeList()
const { theme } = useTheme()

const isOpen = ref(false)

const labels = computed(() => ({
  profile: t('components.common.UserMenu.link.profile'),
  settings: t('components.common.UserMenu.link.settings'),
  logout: t('components.common.UserMenu.link.logout'),
  about: t('components.common.UserMenu.link.about'),
  shortcuts: t('components.common.UserMenu.label.shortcuts'),
  support: t('components.common.UserMenu.link.support'),
  forum: t('components.common.UserMenu.link.forum'),
  docs: t('components.common.UserMenu.link.docs'),
  language: t('components.common.UserMenu.label.language'),
  theme: t('components.common.UserMenu.label.theme'),
  chat: t('components.common.UserMenu.link.chat'),
  git: t('components.common.UserMenu.link.git'),
  login: t('components.common.UserMenu.link.login'),
  signup: t('components.common.UserMenu.link.signup'),
  notifications: t('components.common.UserMenu.link.notifications')
}))
</script>

<template>
  <Popover
    v-model="isOpen"
    raised
  >
    <Button
      round
      square-small
      ghost
      class="user-menu"
      :aria-pressed="isOpen ? true : undefined"
      @click="isOpen = !isOpen"
    >
      <img
        v-if="store.state.auth.authenticated && store.state.auth.profile?.avatar?.urls.small_square_crop"
        alt=""
        :src="store.getters['instance/absoluteUrl'](store.state.auth.profile?.avatar.urls.small_square_crop)"
        class="avatar"
      >
      <span
        v-else-if="store.state.auth.authenticated"
        class="ui tiny avatar circular label"
      >
        {{ store.state.auth.profile?.full_username?.[0] || "" }}
      </span>
      <i
        v-else
        class="bi bi-gear-fill"
      />
    </Button>
    <template #items>
      <PopoverItem
        v-if="store.state.auth.authenticated"
        :to="{name: 'profile.overview', params: { username: store.state.auth.username },}"
      >
        <i class="bi bi-person-fill" />
        {{ labels.profile }}
      </PopoverItem>
      <PopoverItem
        v-if="store.state.auth.authenticated"
        :to="{name: 'notifications'}"
      >
        <i class="bi bi-inbox-fill" />
        {{ labels.notifications }}
        <Spacer grow />
        <div
          v-if="store.state.ui.notifications.inbox > 0"
          :title="labels.notifications"
          style="
            background: var(--fw-gray-400);
            color: var(--fw-gray-800);
            padding: 2px 7px;
            border-radius: 10px;
            font-size: 12px;
          "
        >
          {{ store.state.ui.notifications.inbox }}
        </div>
      </PopoverItem>
      <PopoverItem
        v-if="store.state.auth.authenticated"
        :to="{ path: '/settings' }"
      >
        <i class="bi bi-gear-fill" />
        {{ labels.settings }}
      </PopoverItem>
      <hr v-if="store.state.auth.authenticated">
      <PopoverItem :to="useModal('language').to">
        <i class="bi bi-translate" />
        {{ `${labels.language}...` }}
      </PopoverItem>
      <PopoverSubmenu>
        <i class="bi bi-palette-fill" />
        {{ labels.theme }}
        <template #items>
          <PopoverItem
            v-for="th in themes"
            :key="th.key"
            @click="theme=th.key"
          >
            <i :class="th.icon" />
            {{ th.name }}
          </PopoverItem>
        </template>
      </PopoverSubmenu>
      <hr>
      <PopoverSubmenu>
        <i class="bi bi-question-square-fill" />
        {{ labels.support }}
        <template #items>
          <PopoverItem to="https://forum.funkwhale.audio">
            <i class="bi bi-gear-fill" />
            {{ labels.forum }}
          </PopoverItem>
          <PopoverItem to="https://matrix.to/#/#funkwhale-support:matrix.org">
            <i class="bi bi-chat-left-fill" />
            {{ labels.chat }}
          </PopoverItem>
          <PopoverItem to="https://dev.funkwhale.audio/funkwhale/funkwhale/issues">
            <i class="bi bi-gitlab" />
            {{ labels.git }}
          </PopoverItem>
        </template>
      </PopoverSubmenu>
      <PopoverItem to="https://docs.funkwhale.audio">
        <i class="bi bi-book" />
        {{ labels.docs }}
      </PopoverItem>
      <PopoverItem :to="useModal('shortcuts').to">
        <i class="bi bi-keyboard" />
        {{ labels.shortcuts }}
      </PopoverItem>
      <hr v-if="store.state.auth.authenticated">
      <PopoverItem
        v-if="store.state.auth.authenticated && route.path != '/logout'"
        :to="{ name: 'logout' }"
      >
        <i class="bi bi-box-arrow-right" />
        {{ labels.logout }}
      </PopoverItem>
      <PopoverItem
        v-if="!store.state.auth.authenticated && route.path != '/login'"
        :to="{ name: 'login' }"
      >
        <i class="bi bi-box-arrow-in-right" />
        {{ labels.login }}
      </PopoverItem>
      <PopoverItem
        v-if="!store.state.auth.authenticated && store.state.instance.settings.users.registration_enabled.value"
        :to="{ name: 'signup' }"
      >
        <i class="bi bi-person-square" />
        {{ labels.signup }}
      </PopoverItem>
    </template>
  </Popover>
</template>

<style lang="scss" scoped>
  header > nav button.button {
    padding: 10px;

    &.user-menu {
      padding: 0px !important;

      .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;

        @include light-theme {
          &.label {
            background-color: var(--fw-gray-900);
            color: var(--fw-beige-300);
            &:hover {
              color: var(--fw-color);
              background-color: var(--hover-background-color);
            }
          }
        }

        @include dark-theme {
          &.label {
            background-color: var(--fw-beige-400);
            color: var(--fw-gray-900);
            &:hover {
              color: var(--fw-color);
              background-color: var(--hover-background-color);
            }
          }
        }
      }
    }

  }
  nav.button-list {
    width: 100%;
    a:hover {
      background-color: transparent;
      border: none;
    }
  }
</style>
