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

import Link from '~/components/ui/Link.vue'
import Card from '~/components/ui/Card.vue'
import Button from '~/components/ui/Button.vue'
import Layout from '~/components/ui/Layout.vue'

const store = useStore()
const nodeinfo = computed(() => store.state.instance.nodeinfo)

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
    users: info.usage.users.activeMonth || null,
    hours: info.metadata.content.local.hoursOfContent || null,
    artists: info.metadata.content.local.artists || null,
    albums: info.metadata.content.local.releases || null,
    tracks: info.metadata.content.local.recordings || null,
    listenings: info.metadata.usage?.listenings.total || null
  }

  return { users, hours, data }
})

const openRegistrations = computed(() => get(nodeinfo.value, 'openRegistrations'))

const defaultUploadQuota = computed(() => humanSize(get(nodeinfo.value, 'metadata.defaultUploadQuota', 0) * 1000 * 1000))

const headerStyle = computed(() => {
  if (!banner.value) {
    return ''
  }

  return {
    backgroundImage: `url(${store.getters['instance/absoluteUrl'](banner.value)})`
  }
})

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
  const features = get(nodeinfo.value, 'metadata.metadata.feature', []) as string[]
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
      width="full"
      align-text="stretch"
      style="width:min(480px, 100%)"
    >
      <logo-text />
    </Link>

    <h2 class="header">
      {{ t('components.About.header.funkwhale') }}
    </h2>

    <p>
      {{ t('components.About.description.funkwhale') }}
    </p>

    <Layout
      flex
      style="justify-content: center;"
    >
      <Card
        v-if="!store.state.auth.authenticated"
        :title="t('components.About.header.signup')"
        width="256px"
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
        :title="t('components.About.message.greeting', {username: store.state.auth.username})"
        width="256px"
      >
        <p v-if="defaultUploadQuota">
          {{ t('components.About.description.quota', {quota: defaultUploadQuota}) }}
        </p>

        <template #action>
          <Button
            full
            disabled
          >
            {{ t('components.About.message.loggedIn') }}
          </Button>
        </template>
      </Card>

      <Card
        :title="podName"
        width="256px"
      >
        <section
          :class="['ui', 'head', {'with-background': banner}, 'vertical', 'center', 'aligned', 'stripe', 'segment']"
          :style="headerStyle"
        >
          <h1>
            <i class="music icon" />
          </h1>
        </section>
        <div class="content pod-description">
          <h3
            id="description"
            class="ui header"
          >
            {{ t('components.About.header.aboutPod') }}
          </h3>
          <div
            v-if="shortDescription"
            class="sub header"
          >
            {{ shortDescription }}
          </div>
          <p v-else>
            {{ t('components.About.placeholder.noDescription') }}
          </p>

          <template v-if="stats">
            <div class="statistics-container ui doubling grid">
              <div class="two column row">
                <div class="column">
                  <span class="statistics-figure ui text">
                    <span class="ui big text"><strong>{{ stats.users?.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                    <br>
                    {{ stats.users ? t('components.About.stat.activeUsers', stats.users) : "" }}
                  </span>
                </div>
                <div class="column">
                  <span class="statistics-figure ui text">
                    <span class="ui big text"><strong>{{ stats.hours ? stats.hours.toLocaleString(store.state.ui.momentLocale) : "" }}</strong></span>
                    <br>
                    {{ stats.hours ? t('components.About.stat.hoursOfMusic', stats.hours) : "" }}
                  </span>
                </div>
              </div>
            </div>
          </template>
        </div>

        <template #action>
          <Link
            align-text="center"
            to="/about/pod"
          >
            {{ t('components.About.link.learnMore') }}
          </Link>
        </template>
      </Card>
    </Layout>

    <Layout
      flex
      style="justify-content: center;"
    >
      <Card
        width="256px"
        to="/"
        :title="t('components.About.header.publicContent')"
        icon="bi-box-arrow-up-right"
      >
        <!-- TODO: Link to Explore page? -->
        {{ t('components.About.description.publicContent') }}
      </Card>

      <Card
        width="256px"
        :title="t('components.About.link.findOtherPod')"
        to="https://funkwhale.audio/#get-started"
        icon="bi-box-arrow-up-right"
      >
        {{ t('components.About.description.publicContent') }}
      </Card>

      <Card
        width="256px"
        :title="t('components.About.header.findApp')"
        to="https://funkwhale.audio/apps"
        icon="bi-box-arrow-up-right"
      >
        {{ t('components.About.description.findApp') }}
      </Card>
    </Layout>

    <section
      :class="['ui', 'head', {'with-background': banner}, 'vertical', 'center', 'aligned', 'stripe', 'segment']"
      :style="headerStyle"
    >
      <h1>
        <i class="music icon" />
        {{ podName }}
      </h1>
    </section>

    <!-- About Pod -->
    <div class="about-pod-info-container">
      <div class="about-pod-info-toc">
        <div class="ui vertical pointing secondary menu">
          <router-link
            to="/about/pod"
            class="item"
          >
            {{ t('components.AboutPod.link.about') }}
          </router-link>
          <router-link
            to="/about/pod#rules"
            class="item"
          >
            {{ t('components.AboutPod.link.rules') }}
          </router-link>
          <router-link
            to="/about/pod#terms"
            class="item"
          >
            {{ t('components.AboutPod.link.terms') }}
          </router-link>
          <router-link
            to="/about/pod#features"
            class="item"
          >
            {{ t('components.AboutPod.link.features') }}
          </router-link>
          <router-link
            v-if="stats"
            to="/about/pod#statistics"
            class="item"
          >
            {{ t('components.AboutPod.link.statistics') }}
          </router-link>
        </div>
      </div>

      <div class="about-pod-info">
        <h2
          id="description about-this-pod"
          class="ui header"
        >
          {{ t('components.AboutPod.header.about') }}
        </h2>
        <sanitized-html
          v-if="longDescription"
          :html="longDescription"
        />
        <p v-else>
          {{ t('components.AboutPod.placeholder.noDescription') }}
        </p>

        <h3
          id="rules"
          class="ui header"
        >
          {{ t('components.AboutPod.header.rules') }}
        </h3>
        <sanitized-html
          v-if="rules"
          :html="rules"
        />
        <p v-else>
          {{ t('components.AboutPod.placeholder.noRules') }}
        </p>

        <h3
          id="terms"
          class="ui header"
        >
          {{ t('components.AboutPod.header.terms') }}
        </h3>
        <sanitized-html
          v-if="terms"
          :html="terms"
        />
        <p v-else>
          {{ t('components.AboutPod.placeholder.noTerms') }}
        </p>

        <h3
          id="features"
          class="header"
        >
          {{ t('components.AboutPod.header.features') }}
        </h3>
        <div class="features-container ui two column stackable grid">
          <div class="column">
            <table class="ui very basic table unstackable">
              <tbody>
                <tr>
                  <td>
                    {{ t('components.AboutPod.feature.version') }}
                  </td>
                  <td
                    v-if="version"
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      {{ version }}
                    </span>
                  </td>
                  <td
                    v-else
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      {{ t('components.AboutPod.notApplicable') }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('components.AboutPod.feature.federation') }}
                  </td>
                  <td
                    v-if="federationEnabled"
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="check icon" />
                      {{ t('components.AboutPod.feature.status.enabled') }}
                    </span>
                  </td>
                  <td
                    v-else
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="x icon" />
                      {{ t('components.AboutPod.feature.status.disabled') }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('components.AboutPod.feature.allowList') }}
                  </td>
                  <td
                    v-if="allowListEnabled"
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="check icon" />
                      {{ t('components.AboutPod.feature.status.enabled') }}
                    </span>
                  </td>
                  <td
                    v-else
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="x icon" />
                      {{ t('components.AboutPod.feature.status.disabled') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="column">
            <table class="ui very basic table unstackable">
              <tbody>
                <tr>
                  <td>
                    {{ t('components.AboutPod.feature.anonymousAccess') }}
                  </td>
                  <td
                    v-if="anonymousCanListen"
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="check icon" />
                      {{ t('components.AboutPod.feature.status.enabled') }}
                    </span>
                  </td>
                  <td
                    v-else
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="x icon" />
                      {{ t('components.AboutPod.feature.status.disabled') }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('components.AboutPod.feature.registrations') }}
                  </td>
                  <td
                    v-if="openRegistrations"
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="check icon" />
                      {{ t('components.AboutPod.feature.status.open') }}
                    </span>
                  </td>
                  <td
                    v-else
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      <i class="x icon" />
                      {{ t('components.AboutPod.feature.status.closed') }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td>
                    {{ t('components.AboutPod.feature.quota') }}
                  </td>
                  <td
                    v-if="defaultUploadQuota"
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      {{ defaultUploadQuota }}
                    </span>
                  </td>
                  <td
                    v-else
                    class="right aligned"
                  >
                    <span class="features-status ui text">
                      {{ t('components.AboutPod.notApplicable') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <template v-if="stats">
          <h3
            id="statistics"
            class="header"
          >
            {{ t('components.AboutPod.header.statistics') }}
          </h3>
          <div class="statistics-container">
            <div
              v-if="stats.hours"
              class="statistics-statistic"
            >
              <span class="statistics-figure ui text">
                <span class="ui big text"><strong>{{ stats.hours.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                <br>
                {{ t('components.AboutPod.stat.hoursOfMusic', stats.hours) }}
              </span>
            </div>
            <div
              v-if="stats.data.artists"
              class="statistics-statistic"
            >
              <span class="statistics-figure ui text">
                <span class="ui big text"><strong>{{ stats.data.artists.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                <br>
                {{ t('components.AboutPod.stat.artistsCount', stats.data.artists) }}
              </span>
            </div>
            <div
              v-if="stats.data.albums"
              class="statistics-statistic"
            >
              <span class="statistics-figure ui text">
                <span class="ui big text"><strong>{{ stats.data.albums.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                <br>
                {{ t('components.AboutPod.stat.albumsCount', stats.data.albums) }}
              </span>
            </div>
            <div
              v-if="stats.data.tracks"
              class="statistics-statistic"
            >
              <span class="statistics-figure ui text">
                <span class="ui big text"><strong>{{ stats.data.tracks.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                <br>
                {{ t('components.AboutPod.stat.tracksCount', stats.data.tracks) }}
              </span>
            </div>
            <div
              v-if="stats.users"
              class="statistics-statistic"
            >
              <span class="statistics-figure ui text">
                <span class="ui big text"><strong>{{ stats.users.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                <br>
                {{ t('components.AboutPod.stat.activeUsers', stats.users) }}
              </span>
            </div>
            <div
              v-if="stats.data.listenings"
              class="statistics-statistic"
            >
              <span class="statistics-figure ui text">
                <span class="ui big text"><strong>{{ stats.data.listenings.toLocaleString(store.state.ui.momentLocale) }}</strong></span>
                <br>
                {{ t('components.AboutPod.stat.listeningsCount', stats.data.listenings) }}
              </span>
            </div>
          </div>
        </template>

        <template v-if="contactEmail">
          <h3
            id="contact"
            class="ui header"
          >
            {{ t('components.AboutPod.header.contact') }}
          </h3>
          <a
            v-if="contactEmail"
            :href="`mailto:${contactEmail}`"
          >
            {{ t('components.AboutPod.message.contact', { contactEmail }) }}
          </a>
        </template>

        <div class="ui hidden divider" />
      </div>
    </div>
  </Layout>
</template>
