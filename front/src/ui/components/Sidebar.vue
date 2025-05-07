<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useUploadsStore } from '../stores/upload'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { useModal } from '~/ui/composables/useModal.ts'

import onKeyboardShortcut from '~/composables/onKeyboardShortcut'

import Logo from '~/components/Logo.vue'
import Input from '~/components/ui/Input.vue'
import Link from '~/components/ui/Link.vue'
import UserMenu from './UserMenu.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import { useRoute } from 'vue-router'

const isCollapsed = ref(true)

const route = useRoute()
watch(() => route.path, () => isCollapsed.value = true)

// Hide the fake app when the real one is loaded
onMounted(() => {
  document.getElementById('fake-app')?.remove()
})

const { t } = useI18n()
const { value: searchParameter } = useModal('search')

const store = useStore()
const uploads = useUploadsStore()
const logoUrl = computed(() => store.state.auth.authenticated ? 'library.index' : 'index')

const isOpen = ref(false)

// Search bar focus

const isFocusingSearch = ref<true | undefined>(undefined)
const focusSearch = () => {
  isFocusingSearch.value = undefined
  nextTick(() => {
    isFocusingSearch.value = true
  })
}
onKeyboardShortcut(['shift', 'f'], focusSearch, true)
onKeyboardShortcut(['ctrl', 'k'], focusSearch, true)
onKeyboardShortcut(['/'], focusSearch, true)

// Admin notifications

const moderationNotifications = computed(() =>
  store.state.ui.notifications.pendingReviewEdits
    + store.state.ui.notifications.pendingReviewReports
    + store.state.ui.notifications.pendingReviewRequests
)
</script>

<template>
  <Layout
    aside
    default
    raised
    solid
    gap-12
    :class="[$style.sidebar, $style['sticky-content']]"
  >
    <Layout
      header
      flex
      no-gap
      style="justify-content:space-between; align-items:center; padding-right:8px;"
    >
      <Link
        :to="{name: logoUrl}"
        :class="$style['logo']"
      >
        <i>
          <Logo />
          <span class="visually-hidden">{{ t('components.Sidebar.link.home') }}</span>
        </i>
      </Link>

      <Layout
        nav
        gap-8
        flex
        style="align-items: center;"
      >
        <Popover
          v-if="store.state.auth.availablePermissions['settings'] || store.state.auth.availablePermissions['moderation']"
          v-model="isOpen"
          raised
        >
          <Button
            v-if="store.state.auth.availablePermissions['settings'] || store.state.auth.availablePermissions['moderation']"
            round
            square-small
            ghost
            icon="bi-wrench"
            :aria-pressed="isOpen ? true : undefined"
            @click="isOpen = !isOpen"
          >
            <div
              v-if="moderationNotifications > 0"
              :class="['ui', 'accent', 'mini', 'bottom floating', 'circular', 'label']"
            >
              {{ moderationNotifications }}
            </div>
          </Button>
          <template #items>
            <PopoverItem
              v-if="store.state.auth.availablePermissions['library']"
              :to="{name: 'manage.library.edits', query: {q: 'is_approved:null'}}"
              icon="bi-music-note-beamed"
            >
              {{ t('components.Sidebar.link.library') }}
              <div
                v-if="store.state.ui.notifications.pendingReviewEdits > 0"
                :title="t('components.Sidebar.label.edits')"
                :class="['ui', 'circular', 'mini', 'right floated', 'accent', 'label']"
              >
                {{ store.state.ui.notifications.pendingReviewEdits }}
              </div>
            </PopoverItem>

            <PopoverItem
              v-if="store.state.auth.availablePermissions['moderation']"
              :to="{name: 'manage.moderation.reports.list', query: {q: 'resolved:no'}}"
              icon="bi-megaphone-fill"
            >
              {{ t('components.Sidebar.link.moderation') }}
              <Spacer grow />
              <div
                v-if="store.state.ui.notifications.pendingReviewReports + store.state.ui.notifications.pendingReviewRequests > 0"
                :title="t('components.Sidebar.label.reports')"
                style="
                  background: var(--fw-gray-400);
                  color: var(--fw-gray-800);
                  padding: 2px 7px;
                  border-radius: 10px;
                  font-size: 12px;
                "
              >
                {{ store.state.ui.notifications.pendingReviewReports + store.state.ui.notifications.pendingReviewRequests }}
              </div>
            </PopoverItem>

            <PopoverItem
              v-if="store.state.auth.availablePermissions['settings']"
              :to="{name: 'manage.users.users.list'}"
              icon="bi-people-fill"
            >
              {{ t('components.Sidebar.link.users') }}
            </PopoverItem>

            <PopoverItem
              v-if="store.state.auth.availablePermissions['settings']"
              :to="{path: '/manage/settings'}"
              icon="bi-wrench"
            >
              {{ t('components.Sidebar.link.settings') }}
            </PopoverItem>
          </template>
        </Popover>

        <Link
          v-if="store.state.auth.authenticated"
          round
          square-small
          icon="bi-upload"
          ghost
          :to="useModal('upload').to"
        >
          <Transition>
            <div
              v-if="uploads.currentIndex < uploads.queue.length"
              :class="$style['upload-progress']"
            >
              <div :class="[$style.progress, $style.fake]" />
              <div
                :class="$style.progress"
                :style="{ maxWidth: `${uploads.progress}%` }"
              />
            </div>
          </Transition>
        </Link>

        <UserMenu />

        <Button
          round
          ghost
          square-small
          icon="bi-list large"
          class="hide-on-desktop"
          :class="$style.menu"
          :aria-pressed="isCollapsed ? undefined : true"
          @click="isCollapsed=!isCollapsed"
        />
      </Layout>
    </Layout>
    <Layout
      no-gap
      stack
      :class="[$style['menu-links'], isCollapsed && 'hide-on-mobile']"
    >
      <Input
        :key="isFocusingSearch ? 1 : 0"
        v-model="searchParameter"
        :autofocus="isFocusingSearch"
        raised
        autocomplete="search"
        type="search"
        icon="bi-search"
        :placeholder="t('components.audio.SearchBar.placeholder.search')"
      />

      <Spacer />

      <!-- Sign up, Log in -->
      <div
        v-if="!store.state.auth.authenticated"
        style="display: contents;"
      >
        <Layout
          flex
          gap-16
        >
          <Link
            :to="{ name: 'login' }"
            solid
            auto
            grow
            icon="bi-box-arrow-in-right"
            class="active"
          >
            {{ t('components.common.UserMenu.link.login') }}
          </Link>
          <Link
            :to="{ name: 'signup' }"
            default
            solid
            auto
            grow
            icon="bi-person-square"
          >
            {{ t('components.common.UserMenu.link.signup') }}
          </Link>
        </Layout>
        <Spacer grow />
      </div>

      <nav style="display:grid;">
        <Link
          to="/library"
          ghost
          full
          align-text="start"
          icon="bi-compass"
          thick-when-active
        >
          {{ t('components.Sidebar.header.explore') }}
        </Link>

        <Link
          to="/library/artists"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-person-circle"
          thick-when-active
        >
          {{ t('components.Sidebar.link.artists') }}
        </Link>

        <Link
          to="/library/channels"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-person-square"
          thick-when-active
        >
          {{ t('components.Sidebar.link.channels') }}
        </Link>

        <Link
          to="/library/albums"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-disc"
          thick-when-active
        >
          {{ t('components.Sidebar.link.albums') }}
        </Link>

        <Link
          to="/library/playlists"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-music-note-list"
          thick-when-active
        >
          {{ t('components.Sidebar.link.playlists') }}
        </Link>
        <Link
          to="/library/radios"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-boombox-fill"
          thick-when-active
        >
          {{ t('components.Sidebar.link.radios') }}
        </Link>
        <Link
          to="/library/podcasts"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-mic"
          thick-when-active
        >
          {{ t('components.Sidebar.link.podcasts') }}
        </Link>
        <Link
          to="/favorites"
          ghost
          full
          align-text="start"
          thin-font
          icon="bi-heart"
          thick-when-active
          :disabled="!store.state.auth.authenticated || undefined"
        >
          {{ t('components.Sidebar.link.favorites') }}
        </Link>
      </nav>
      <Spacer grow />
      <Layout
        nav
        flex
        no-gap
        style="justify-content: center"
      >
        <Link
          thin-font
          to="/about"
        >
          {{ t('components.Sidebar.link.about') }}
        </Link>
        <Spacer shrink />
      </Layout>
    </Layout>
  </Layout>
</template>

<style module lang="scss">
.sidebar {
  .logo {
    display: block;
    width: 40px;
    height: 40px;
    margin: 16px;
  }

  &.sticky-content {
    overflow: auto;
    top: 0;

    .upload-progress {
      background: var(--fw-blue-500);
      position: absolute;
      left: 0;
      bottom: 2px;
      width: 100%;
      padding: 2px;

      &.v-enter-active,
      &.v-leave-active {
        transition: transform 0.2s ease, opacity 0.2s ease;
      }

      &.v-leave-to,
      &.v-enter-from {
        transform: translateY(0.5rem);
        opacity: 0;
      }

      > .progress {
        height: 0.25rem;
        width: 100%;
        transition: max-width 0.1s ease;
        background: var(--fw-gray-100);
        border-radius: 100vh;
        position: relative;

        &.fake {
          background: var(--fw-blue-700);
        }

        &:not(.fake) {
          position: absolute;
          inset: 2px;
        }
      }
    }

    .avatar {
      aspect-ratio: 1;
      background: var(--fw-beige-100);
      border-radius: 100%;

      text-decoration: none !important;
      color: var(--fw-gray-700);

      > img,
      > i {
        width: 100%;
        height: 100%;

        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 !important;
        border-radius: 100vh;
      }
    }

    > h3 {
      margin: 0;
      padding: 0 32px 8px;
      font-size: 14px;
      line-height: 1.2;
    }
    .menu-links {
      // Bottom padding is mainly offsetting player-bar
      padding: 0 16px 72px;
      flex-grow: 1;
    }
  }

  :global(.hide-on-mobile) {
    max-height: 0px;
    min-height: 0px;
    overflow: hidden;
    transition: all .8s;
  }

  @media screen and (min-width: 1024px) {
    height: 100%;

    :global(.hide-on-desktop) {
      display: none !important;
    }

    :global(.hide-on-mobile) {
      max-height: 100dvh;
      pointer-events: unset;
    }

    &.sticky-content {
      position: sticky;
      max-height: 100dvh;
    }
  }
}
</style>
