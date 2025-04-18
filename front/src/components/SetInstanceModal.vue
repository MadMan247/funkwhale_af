<script setup lang="ts">
import Modal from '~/components/ui/Modal.vue'
import axios from 'axios'
import { uniq } from 'lodash-es'
import { useVModel } from '@vueuse/core'
import { ref, computed, watch, nextTick } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

// TODO: Delete this file?

const { t } = useI18n()

interface Props {
  show: boolean
}

const props = defineProps<Props>()

const emit = defineEmits(['update:show'])
const show = useVModel(props, 'show', emit)

const instanceUrl = ref('')

const store = useStore()
const suggestedInstances = computed(() => {
  const serverUrl = store.state.instance.frontSettings.defaultServerUrl

  return uniq([
    store.state.instance.instanceUrl,
    ...store.state.instance.knownInstances,
    serverUrl.endsWith('/') ? serverUrl : serverUrl + '/',
    store.getters['instance/defaultInstance']
  ]).slice(1)
})

watch(() => store.state.instance.instanceUrl, () => store.dispatch('instance/fetchSettings'))

// TODO: replace translation mechanism { $pgettext } with { t }

// const { $pgettext } = useGettext()
const isError = ref(false)
const isLoading = ref(false)
const checkAndSwitch = async (url: string) => {
  isError.value = false
  isLoading.value = true

  try {
    const instanceUrl = new URL(url.startsWith('https://') || url.startsWith('http://') ? url : `https://${url}`).origin
    await axios.get(instanceUrl + '/api/v1/instance/nodeinfo/2.0/')

    show.value = false
    store.commit('ui/addMessage', {
      content: 'You are now using the Funkwhale instance at %{ url }',
      // $pgettext('*/Instance/Message', 'You are now using the Funkwhale instance at %{ url }', { url: instanceUrl }),
      date: new Date()
    })

    await nextTick()
    store.dispatch('instance/setUrl', instanceUrl)
  } catch (error) {
    isError.value = true
  }

  isLoading.value = false
}
</script>

<template>
  <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
  <Modal
    v-model="show"
    :title="t('views.ChooseInstance.header.chooseInstance')"
    @update="isError = false"
  >
    <h3 class="header">
      <!-- TODO: translate -->

      <!-- <translate translate-context="Popup/Instance/Title">
      </translate> -->
    </h3>
    <div class="scrolling content">
      <div
        v-if="isError"
        role="alert"
        class="ui negative message"
      >
        <h4 class="header">
          <!-- TODO: translate -->
          It is not possible to connect to the given URL
          <!-- <translate translate-context="Popup/Instance/Error message.Title">
          </translate> -->
        </h4>
        <ul class="list">
          <li>
            <!-- TODO: translate -->
            The server might be down
            <!-- <translate translate-context="Popup/Instance/Error message.List item">
            </translate> -->
          </li>
          <li>
            <!-- TODO: translate -->
            The given address is not a Funkwhale server
            <!-- <translate translate-context="Popup/Instance/Error message.List item">
            </translate> -->
          </li>
        </ul>
      </div>
      <form
        class="ui form"
        @submit.prevent="checkAndSwitch(instanceUrl)"
      >
        <p
          v-if="store.state.instance.instanceUrl"
          v-translate="{url: store.state.instance.instanceUrl, hostname: store.getters['instance/domain'] }"
          class="description"
          translate-context="Popup/Login/Paragraph"
        >
          You are currently connected to <a
            href="%{ url }"
            target="_blank"
          >%{ hostname }&nbsp;<i class="external icon" /></a>. If you continue, you will be disconnected from your current instance and all your local data will be deleted.
        </p>
        <p v-else>
          <!-- TODO: translate -->
          To continue, please select the Funkwhale instance you want to connect to. Enter the address directly, or select one of the suggested choices.
          <!-- <translate translate-context="Popup/Instance/Paragraph">
          </translate> -->
        </p>
        <div class="field">
          <label for="instance-picker">
            <!-- TODO: translate -->
            <!-- <translate translate-context="Popup/Instance/Input.Label/Noun">Instance URL</translate>
            -->
          </label>
          <div class="ui action input">
            <input
              id="instance-picker"
              v-model="instanceUrl"
              type="text"
              placeholder="https://funkwhale.server"
            >
            <button
              type="submit"
              :class="['ui', 'icon', {loading: isLoading}, 'button']"
            >
              <!-- TODO: translate -->
              Submit
              <!-- <translate translate-context="*/*/Button.Label/Verb">
              </translate> -->
            </button>
          </div>
        </div>
      </form>
      <div class="ui hidden divider" />
      <form
        class="ui form"
        @submit.prevent=""
      >
        <div class="field">
          <h4>
            <!-- TODO: translate -->
            Suggested choices
            <!-- <translate translate-context="Popup/Instance/List.Label">
            </translate> -->
          </h4>
          <button
            v-for="(url, key) in suggestedInstances"
            :key="key"
            class="ui basic button"
            @click="checkAndSwitch(url)"
          >
            {{ url }}
          </button>
        </div>
      </form>
    </div>
    <div class="actions">
      <button class="ui basic cancel button">
        <!-- TODO: translate -->
        Cancel
        <!-- <translate translate-context="*/*/Button.Label/Verb">
        </translate> -->
      </button>
    </div>
  </Modal>
  <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
</template>
