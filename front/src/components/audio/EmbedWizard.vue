<script setup lang="ts">
import { get } from 'lodash-es'
import { ref, computed } from 'vue'
import { useStore } from '~/store'
import { useClipboard } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import Button from '~/components/ui/Button.vue'
import Alert from '~/components/ui/Alert.vue'
import Input from '~/components/ui/Input.vue'
import Spacer from '~/components/ui/Spacer.vue'

interface Props {
  type: string
  id?: number
  uuid?: string
}

const { t } = useI18n()

const props = defineProps<Props>()

// TODO: This used to be `null`. Is `0` correct?
const width = ref(0)

const height = ref(150)
const minHeight = ref(100)

if (props.type === 'album' || props.type === 'artist' || props.type === 'playlist') {
  height.value = 330
  minHeight.value = 250
}

const store = useStore()
const nodeinfo = computed(() => store.state.instance.nodeinfo)
const anonymousCanListen = computed(() => get(nodeinfo.value, 'metadata.library.anonymousCanListen', false))
const iframeSrc = computed(() => {
  const base = import.meta.env.BASE_URL.startsWith('/')
    ? `${window.location.origin}${import.meta.env.BASE_URL}`
    : import.meta.env.BASE_URL

  const instanceUrl = store.state.instance.instanceUrl as string

  const bParam = !window.location.href.startsWith(instanceUrl)
    ? `&b=${instanceUrl}`
    : ''

  const identifier = props.id ?? props.uuid
  return `${base}embed.html?&type=${props.type}&id=${identifier}${bParam}`
})

const frameWidth = computed(() => width.value ?? '100%')
const embedCode = computed(() => `<iframe width="${frameWidth.value}" height="${height.value}" scrolling="no" frameborder="no" src="${iframeSrc.value.replace(/&/g, '&amp;')}"></iframe>`)

const { copy, copied } = useClipboard({ source: embedCode })
</script>

<template>
  <div>
    <div
      v-if="!anonymousCanListen"
      role="alert"
      class="ui warning message"
    >
      <p>
        <strong>
          {{ t('components.audio.EmbedWizard.warning.anonymous') }}
        </strong>
      </p>
      <p>
        {{ t('components.audio.EmbedWizard.help.anonymous') }}
      </p>
    </div>
    <div class="ui form">
      <div class="two fields">
        <div class="field">
          <div class="field">
            <label for="embed-width">{{ t('components.audio.EmbedWizard.label.width') }}</label>
            <p>
              {{ t('components.audio.EmbedWizard.help.width') }}
            </p>
            <Input
              id="embed-width"
              v-model.number="width"
              type="number"
              min="0"
              step="10"
            />
          </div>
          <template v-if="type != 'track'">
            <br>
            <div class="field">
              <label for="embed-height">{{ t('components.audio.EmbedWizard.label.height') }}</label>
              <Input
                id="embed-height"
                v-model="height"
                type="number"
                :min="minHeight"
                max="1000"
                step="10"
              />
            </div>
          </template>
        </div>
        <Spacer />
        <div class="field">
          <Button
            class="right floated"
            icon="bi-copy"
            secondary
            @click="copy()"
          >
            {{ t('components.audio.EmbedWizard.button.copy') }}
          </Button>
          <label for="embed-width">{{ t('components.audio.EmbedWizard.label.embed') }}</label>
          <p>
            {{ t('components.audio.EmbedWizard.help.embed') }}
          </p>
          <textarea
            v-model="embedCode"
            rows="3"
            readonly
            style="width: 100%;"
          />
          <Alert
            v-if="copied"
            green
          >
            {{ t('components.audio.EmbedWizard.message.copy') }}
          </Alert>
        </div>
      </div>
    </div>
    <div class="preview">
      <h3>
        <a
          :href="iframeSrc"
          target="_blank"
        >
          {{ t('components.audio.EmbedWizard.header.preview') }}
        </a>
      </h3>
      <iframe
        :width="frameWidth"
        :height="height"
        scrolling="no"
        frameborder="no"
        :src="iframeSrc"
      />
    </div>
  </div>
</template>
