<script setup lang="ts">
import type { Album, ArtistCredit, Library } from '~/types'

import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import { getDomain } from '~/utils'

import useReport from '~/composables/moderation/useReport'

import EmbedWizard from '~/components/audio/EmbedWizard.vue'

import Modal from '~/components/ui/Modal.vue'
import Popover from '~/components/ui/Popover.vue'
import PopoverItem from '~/components/ui/popover/PopoverItem.vue'
import OptionsButton from '~/components/ui/button/Options.vue'

interface Props {
  isLoading: boolean
  artistCredit: ArtistCredit[]
  object: Album
  publicLibraries: Library[]
  isAlbum: boolean
  isChannel: boolean
  isSerie: boolean

}

const store = useStore()
const props = defineProps<Props>()
const { report, getReportableObjects } = useReport()

const showEmbedModal = ref(false)

const domain = computed(() => getDomain(props.object.fid))

const { t } = useI18n()
const labels = computed(() => ({
  more: t('components.library.AlbumDropdown.button.more')
}))

// TODO: What is the condition for an album to be embeddable?
// (a) props.publicLibraries.length
// (b) I am the channel's artist: props.isChannel && props.artistCredit[0].artist?.channel?.actor)
const isEmbedable = computed(() => (props.publicLibraries.length))
const musicbrainzUrl = computed(() => props.object?.mbid ? `https://musicbrainz.org/release/${props.object.mbid}` : null)
const discogsUrl = computed(() => `https://discogs.com/search/?type=release&title=${encodeURI(props.object?.title)}&artist=${encodeURI(props.object?.artist_credit[0].artist.name)}`)

const open = ref(false)
</script>

<template>
  <span>
    <Modal
      v-if="isEmbedable"
      v-model="showEmbedModal"
      :title="t('components.library.AlbumDropdown.modal.embed.header')"
      :cancel="t('components.library.AlbumDropdown.button.cancel')"
    >
      <div class="scrolling content">
        <div class="description">
          <embed-wizard
            :id="object.id"
            type="album"
          />
        </div>
      </div>
    </Modal>
    <Popover v-model="open">
      <template #default="{ toggleOpen }">
        <OptionsButton
          :title="labels.more"
          is-square-small
          @click="toggleOpen()"
        />
      </template>

      <template #items>
        <PopoverItem
          v-if="domain != store.getters['instance/domain']"
          :to="object.fid"
          icon="bi-box-arrow-up-right"
          target="_blank"
        >
          {{ t('components.library.AlbumDropdown.link.domain') }}
        </PopoverItem>

        <PopoverItem
          v-if="isEmbedable"
          icon="bi-code"
          @click="showEmbedModal = !showEmbedModal"
        >
          {{ t('components.library.AlbumDropdown.button.embed') }}
        </PopoverItem>

        <PopoverItem
          v-if="isAlbum && musicbrainzUrl"
          :to="musicbrainzUrl"
          icon="bi-box-arrow-up-right"
          target="_blank"
          rel="noreferrer noopener"
        >
          {{ t('components.library.AlbumDropdown.link.musicbrainz') }}
        </PopoverItem>

        <PopoverItem
          v-if="!isChannel && isAlbum"
          :to="discogsUrl"
          icon="bi-box-arrow-up-right"
          target="_blank"
          rel="noreferrer noopener"
        >
          {{ t('components.library.AlbumDropdown.link.discogs') }}
        </PopoverItem>

        <PopoverItem
          v-if="object.is_local"
          :to="{ name: 'library.albums.edit', params: { id: object.id } }"
          icon="bi-pencil"
        >
          {{ t('components.library.AlbumDropdown.button.edit') }}
        </PopoverItem>

        <hr>

        <PopoverItem
          v-for="obj in getReportableObjects({
            album: object
            /*

            TODO: The type of the following field has changed to number.
            Find out if we want to load the corresponding channel instead.

            , channel: artistCredit[0]?.artist.channel
            */
          })"
          :key="obj.target.type + obj.target.id"
          icon="bi-flag"
          @click="report(obj)"
        >
          {{ obj.label }}
        </PopoverItem>

        <hr>

        <PopoverItem
          v-if="store.state.auth.availablePermissions['library']"
          :to="{
            name: 'manage.library.albums.detail',
            params: { id: object.id }
          }"
          icon="bi-wrench"
        >
          {{ t('components.library.AlbumDropdown.link.moderation') }}
        </PopoverItem>

        <PopoverItem
          v-if="store.state.auth.profile?.is_superuser"
          :to="store.getters['instance/absoluteUrl'](`/api/admin/music/album/${object.id}`)"
          icon="bi-wrench"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ t('components.library.AlbumDropdown.link.django') }}
        </PopoverItem>
      </template>
    </Popover>
  </span>
</template>
