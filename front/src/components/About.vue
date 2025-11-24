<script setup lang="ts">
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { get } from 'lodash-es'
import { humanSize } from '~/utils/filters'
import { computed } from 'vue'

import type { components } from '~/generated/types.ts'

import SignupForm from '~/components/auth/SignupForm.vue'
import LogoText from '~/components/LogoText.vue'
import useMarkdown from '~/composables/useMarkdown'
import { useModal } from '~/ui/composables/useModal.ts'

import HeaderImage from './HeaderImage.vue'

import Link from '~/components/ui/Link.vue'
import Card from '~/components/ui/Card.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Modal from '~/components/ui/Modal.vue'
import Table from '~/components/ui/Table.vue'
import SanitizedHtml from '~/components/ui/SanitizedHtml.vue'
import Heading from '~/components/ui/Heading.vue'

const store = useStore()
const nodeinfo = computed(() => store.state.instance.nodeinfo)

// Problem: When binding this to a CSS variable, it is only available in the current DOM nodes and its descendants. We cannot use it as a CSS variable in a teleported `<Modal>`.
const backgroundImage = computed(() =>
  banner.value
    ? `url(${store.getters['instance/absoluteUrl'](banner.value)})`
    : 'radial-gradient(circle at 80%, rgb(55, 122, 170), transparent), linear-gradient(135deg, rgb(40, 88, 125) 0%, rgb(64, 190, 220) 100%)'
)

const { isOpen, to } = useModal('pod')
const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.About.title')
}))

const podName = computed(() => (n => n === '' ? 'No name' : n ?? 'Funkwhale')(get(nodeinfo.value, 'metadata.nodeName')))

const banner = computed(() => get(nodeinfo.value, 'metadata.banner'))
const shortDescription = computed(() => get(nodeinfo.value, 'metadata.shortDescription'))

const stats = computed(() => {
  const users = get(nodeinfo.value, 'usage.users.activeMonth', 0)
  const hours = get(nodeinfo.value, 'metadata.library.music.hours', 0)

  if (users === null) {
    return null
  }

  const info = nodeinfo.value ?? {} as components['schemas']['NodeInfo21']

  const data = {
    users: info.usage?.users.activeMonth || null,
    hours: info.metadata?.content.local.hoursOfContent || null,
    artists: info.metadata?.content.local.artists || null,
    albums: info.metadata?.content.local.releases || null,
    tracks: info.metadata?.content.local.recordings || null,
    listenings: info.metadata?.usage?.listenings.total || null
  }

  return { users, hours, data }
})

const openRegistrations = computed(() => get(nodeinfo.value, 'openRegistrations'))

const defaultUploadQuota = computed(() => humanSize(get(nodeinfo.value, 'metadata.defaultUploadQuota', 0) * 1000 * 1000))

const longDescription = useMarkdown(() => get(nodeinfo.value, 'metadata.longDescription', ''))
const rules = useMarkdown(() => get(nodeinfo.value, 'metadata.rules', ''))
const terms = useMarkdown(() => get(nodeinfo.value, 'metadata.terms', ''))
const contactEmail = computed(() => get(nodeinfo.value, 'metadata.contactEmail'))
const anonymousCanListen = computed(() => {
  const features = get(nodeinfo.value, 'metadata.metadata.feature', []) as string[]
  const hasAnonymousCanListen = features.includes('anonymousCanListen')
  return hasAnonymousCanListen
})
const allowListEnabled = computed(() => get(nodeinfo.value, 'metadata.allowList.enabled'))
const version = computed(() => get(nodeinfo.value, 'software.version'))
const federationEnabled = computed(() => {
  const features = get(nodeinfo.value, 'metadata.features', []) as string[]
  const hasAnonymousCanListen = features.includes('federation')
  return hasAnonymousCanListen
})
</script>

<template>
  <Layout
    v-title="labels.title"
    stack
    main
    style="align-items: center;"
  >
    <!-- About funkwhale -->

    <Link
      to="/"
    >
      <LogoText style="width: 100%;" />
    </Link>

    <h2 class="header">
      {{ t('components.About.header.funkwhale') }}
    </h2>

    <p>
      {{ t('components.About.description.funkwhale') }}
    </p>

    <!-- Top row -->
    <Layout
      flex
      style="justify-content: center;"
    >
      <!-- Login / Greeting Card -->

      <Card
        v-if="!store.state.auth.authenticated"
        small
        flat
        blue
        solid
        :title="t('components.About.header.signup')"
      >
        <template v-if="openRegistrations">
          <p>
            {{ t('components.About.description.signup') }}
          </p>
          <p v-if="defaultUploadQuota">
            {{ t('components.About.description.quota', {quota: defaultUploadQuota}) }}
          </p>
          <signup-form
            button-classes="success"
            :show-login="true"
          />
        </template>

        <div v-else>
          <p>
            {{ t('components.About.help.closedRegistrations') }}
          </p>

          <a
            target="_blank"
            rel="noopener"
            href="https://funkwhale.audio/#get-started"
          >
            {{ t('components.About.link.findOtherPod') }}
            &nbsp;<i class="external alternate icon" />
          </a>
        </div>

        <div
          v-if="!(store.state.auth.authenticated || openRegistrations)"
          class="signup-form content"
        >
          <h3 class="header">
            {{ t('components.About.header.signup') }}
            <div class="ui positive message">
              <div class="header">
                {{ t('components.About.message.loggedIn') }}
              </div>
              <p>
                {{ t('components.About.message.greeting', {username: store.state.auth.username}) }}
              </p>
            </div>
          </h3>
        </div>
      </Card>

      <Card
        v-else
        flat
        solid
        :title="t('components.About.message.greeting', {username: store.state.auth.username})"
      >
        <p v-if="defaultUploadQuota">
          {{ t('components.About.description.quota', {quota: defaultUploadQuota}) }}
        </p>

        <template #action>
          <Button
            full
            disabled
            :title="t('components.About.message.loggedIn')"
            style="opacity:0;"
          />
        </template>
      </Card>

      <!-- Pod Card and modal -->
      <Card
        :to
        solid
        primary
        :title=" t('components.About.header.aboutPod')"
        icon="bi-music-note-beamed"
      >
        <template #image>
          <HeaderImage
            :title="podName"
            :background-image
          />
        </template>
        <div :class="$style.noUnderline">
          <div
            v-if="shortDescription"
          >
            {{ shortDescription }}
          </div>
          <p v-else>
            {{ t('components.About.placeholder.noDescription') }}
          </p>
          <Spacer size-8 />
          <hr>
          <Spacer size-8 />

          <Layout
            v-if="stats"
            flex
            style="justify-content:space-evenly"
          >
            <div v-if="stats.hours">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500); text-decoration-color: transparent !important;">
                {{ stats.hours.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px; text-decoration-color:transparent !important;">
                {{ t('components.AboutPod.stat.hoursOfMusic', stats.hours) }}
              </div>
            </div>

            <div v-if="stats.users">
              <div style="font-size: 28px; font-weight: 700; color: var(--color); opacity: .5; text-decoration-color: transparent !important;">
                {{ stats.users.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px; text-decoration-color: transparent !important;">
                {{ t('components.AboutPod.stat.activeUsers', stats.users) }}
              </div>
            </div>
          </Layout>
          <Spacer size-8 />
          <hr>
        </div>


        <Heading
          caption
          :h2=" t('components.About.link.learnMore')"
        />
      </Card>
    </Layout>

    <Layout
      flex
      style="justify-content: center;"
    >
      <Card
        to="/"
        :title="t('components.About.header.publicContent')"
        icon="bi-box-arrow-up-right"
      >
        <!-- TODO: Link to Explore page? -->
        {{ t('components.About.description.publicContent') }}
      </Card>

      <Card
        to="https://funkwhale.audio/#get-started"
        :title="t('components.About.link.findOtherPod')"
        icon="bi-box-arrow-up-right"
      >
        {{ t('components.About.description.publicContent') }}
      </Card>

      <Card
        to="https://funkwhale.audio/apps"
        :title="t('components.About.header.findApp')"
        icon="bi-box-arrow-up-right"
      >
        {{ t('components.About.description.findApp') }}
      </Card>
    </Layout>

    <!-- About Pod -->

    <Modal
      v-model="isOpen"
      title=""
      raised
      solid
    >
      <HeaderImage
        :title="podName"
        :background-image
        icon="bi-music-note-beamed"
        overflowing
      />
      <Layout grid>
        <!-- Pod Description Card -->
        <Card
          :title=" t('components.About.header.aboutPod')"
          icon="bi-info-circle-fill large"
          solid
          secondary
          :class="{ [$style.multiRow]: longDescription }"
          :full="longDescription.length > 600 || undefined"
        >
          <SanitizedHtml
            v-if="longDescription"
            :html="longDescription"
          />
          <p v-else>
            {{ t('components.AboutPod.placeholder.noDescription') }}
          </p>
        </Card>

        <!-- Rules Card -->
        <Card
          solid
          :title="t('components.AboutPod.header.rules')"
          icon="bi-flag-fill"
          :class="{ [$style.multiRow]: rules }"
          :full="rules.length > 600 || undefined"
        >
          <SanitizedHtml
            v-if="rules"
            :html="rules"
          />
          <p v-else>
            {{ t('components.AboutPod.placeholder.noRules') }}
          </p>
        </Card>

        <!-- Terms Card -->
        <Card
          solid
          :title="t('components.AboutPod.header.terms')"
          icon="bi-shield-shaded"
          :class="{ [$style.multiRow]: terms }"
          :full="terms.length > 600 || undefined"
        >
          <SanitizedHtml
            v-if="terms"
            :html="terms"
          />
          <p v-else>
            {{ t('components.AboutPod.placeholder.noTerms') }}
          </p>
        </Card>

        <!-- Features Card -->
        <Card
          solid
          :title="t('components.AboutPod.header.features')"
          icon="bi-gear-fill"
          :class="{ [$style.multiRow]: true }"
        >
          <Table :grid-template-columns="['1fr', 'auto']">
            <span>{{ t('components.AboutPod.feature.version') }}</span>
            <span v-if="version">{{ version }}</span>
            <span v-else>{{ t('components.AboutPod.notApplicable') }}</span>

            <span>{{ t('components.AboutPod.feature.federation') }}</span>
            <span v-if="federationEnabled">
              <i
                class="bi bi-check-circle-fill"
                style="color: var(--fw-pastel-green-4);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.enabled') }}
            </span>
            <span v-else>
              <i
                class="bi bi-x-circle-fill"
                style="color: var(--fw-red-500);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.disabled') }}
            </span>

            <span>{{ t('components.AboutPod.feature.allowList') }}</span>
            <span v-if="allowListEnabled">
              <i
                class="bi bi-check-circle-fill"
                style="color: var(--fw-pastel-green-4);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.enabled') }}
            </span>
            <span v-else>
              <i
                class="bi bi-x-circle-fill"
                style="color: var(--fw-red-500);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.disabled') }}
            </span>

            <span>{{ t('components.AboutPod.feature.anonymousAccess') }}</span>
            <span v-if="anonymousCanListen">
              <i
                class="bi bi-check-circle-fill"
                style="color: var(--fw-pastel-green-4);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.enabled') }}
            </span>
            <span v-else>
              <i
                class="bi bi-x-circle-fill"
                style="color: var(--fw-red-500);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.disabled') }}
            </span>

            <span>{{ t('components.AboutPod.feature.registrations') }}</span>
            <span v-if="openRegistrations">
              <i
                class="bi bi-check-circle-fill"
                style="color: var(--fw-pastel-green-4);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.open') }}
            </span>
            <span v-else>
              <i
                class="bi bi-x-circle-fill"
                style="color: var(--fw-red-500);"
              />&nbsp;
              {{ t('components.AboutPod.feature.status.closed') }}
            </span>

            <span>{{ t('components.AboutPod.feature.quota') }}</span>
            <span v-if="defaultUploadQuota">{{ defaultUploadQuota }}</span>
            <span v-else>{{ t('components.AboutPod.notApplicable') }}</span>
          </Table>
        </Card>

        <!-- Statistics Card -->
        <Card
          v-if="stats"
          :title="t('components.AboutPod.header.statistics')"
          solid
          icon="bi-bar-chart-fill"
          :class="{ [$style.multiRow]: true }"
        >
          <Spacer size-16 />
          <Layout
            flex
            style="justify-content:space-evenly"
          >
            <div v-if="stats.hours">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500);">
                {{ stats.hours.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px;">
                {{ t('components.AboutPod.stat.hoursOfMusic', stats.hours) }}
              </div>
            </div>

            <div v-if="stats.data.artists">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500);">
                {{ stats.data.artists.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px;">
                {{ t('components.AboutPod.stat.artistsCount', stats.data.artists) }}
              </div>
            </div>

            <div v-if="stats.data.albums">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500);">
                {{ stats.data.albums.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px;">
                {{ t('components.AboutPod.stat.albumsCount', stats.data.albums) }}
              </div>
            </div>

            <div v-if="stats.data.tracks">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500);">
                {{ stats.data.tracks.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px;">
                {{ t('components.AboutPod.stat.tracksCount', stats.data.tracks) }}
              </div>
            </div>

            <div v-if="stats.users">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500);">
                {{ stats.users.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px;">
                {{ t('components.AboutPod.stat.activeUsers', stats.users) }}
              </div>
            </div>

            <div v-if="stats.data.listenings">
              <div style="font-size: 28px; font-weight: 700; color: var(--fw-blue-500);">
                {{ stats.data.listenings.toLocaleString(store.state.ui.momentLocale) }}
              </div>
              <div style="font-size: 14px;">
                {{ t('components.AboutPod.stat.listeningsCount', stats.data.listenings) }}
              </div>
            </div>
          </Layout>
        </Card>

        <!-- Contact Card -->
        <Card
          v-if="contactEmail"
          solid
          primary
          :title="t('components.AboutPod.header.contact')"
          icon="bi-envelope-fill large"
          :class="{ [$style.multiRow]: true }"
          :to="`mailto:${contactEmail}`"
        >
          <p>
            {{ t('components.AboutPod.message.contact', { contactEmail }) }}
          </p>
        </Card>
      </Layout>
    </Modal>
  </Layout>
</template>

<style module>
    .multiRow {
        grid-row: span 2;
    }

    /* TODO: This does not work (Firefox v141.0.3, NixOS Linux) */
    .noUnderline, .noUnderline div,  :hover .noUnderline * {
        text-decoration-color: transparent !important;

        hr { border-color: var(--color); }
    }

</style>
