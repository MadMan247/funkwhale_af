<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import { type Track, type User } from '~/types'

import OptionsButton from '~/components/ui/button/Options.vue'
import PlayButton from '~/components/ui/button/Play.vue'

// TODO (2.0.0+): Move into app namespace because this component uses funkwhale types

const { t } = useI18n()

const emit = defineEmits<{ play: [track: Track] }>()

const { track, user } = defineProps<{ track: Track, user: User }>()

const router = useRouter()

const navigate = (to: 'track' | 'user') =>
  to === 'track'
    ? router.push({ name: 'library.tracks.detail', params: { id: track.id } })
    : router.push({ name: 'profile.full', params: profileParams.value })

const profileParams = computed(() => {
  const [username, domain] = user.full_username.split('@')
  return { username, domain }
})
</script>

<template>
  <div
    class="funkwhale activity"
    @click="navigate('track')"
  >
    <div class="activity-image">
      <img :src="track.cover?.urls.original">
      <PlayButton
        :round="false"
        :shadow="false"
        @play="emit('play', track)"
      />
    </div>
    <div class="activity-content">
      <div class="track-title">
        {{ track.title }}
      </div>
      <a
        v-for="{ artist } in track.artist_credit"
        :key="artist.id"
        class="funkwhale link artist"
        @click.stop="router.push({
          name: 'library.artists.detail',
          params: { id: artist.id }
        })"
      >
        {{ artist.name }}
      </a>
      <a
        class="funkwhale link user"
        @click.stop="navigate('user')"
      >
        {{ t('vui.by-user', { username: user.username }) }}
      </a>
    </div>
    <div>
      <OptionsButton />
    </div>
  </div>
</template>

<style lang="scss">
@use '~/style/funkwhale.scss';

.funkwhale {
  &.activity {
    padding: 0 16px;
    height: 72px;
    display: flex;
    align-items: center;
    border-top: 1px solid;
    cursor: pointer;
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 12px;
    grid-column: span 4;

    &.clickable {
      cursor: pointer;
    }

    @include funkwhale.light-theme {
      color: var(--fw-gray-500);

      +.funkwhale.activity {
        border-top: 1px solid var(--fw-gray-300);
      }

      >.activity-content {
        >.track-title {
          color: var(--fw-gray-900);
        }

        >.artist {
          --fw-link-color: var(--fw-gray-900);
        }

        >.user {
          --fw-link-color: var(--fw-gray-500);
        }
      }

      .play-button {
        background: rgba(255, 255, 255, .5);

        &:hover {
          --fw-text-color: var(--fw-gray-800) !important;
        }
      }
    }

    @include funkwhale.dark-theme {
      +.funkwhale.activity {
        border-top: 1px solid var(--fw-gray-800);
      }
    }
  }
}
</style>
