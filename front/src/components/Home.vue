<script setup lang="ts">
import { get } from 'lodash-es'
import AlbumWidget from '~/components/album/Widget.vue'
import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import LoginForm from '~/components/auth/LoginForm.vue'
import SignupForm from '~/components/auth/SignupForm.vue'
import useMarkdown from '~/composables/useMarkdown'
import useLogger from '~/composables/useLogger'
import { humanSize } from '~/utils/filters'
import { useStore } from '~/store'
import { computed } from 'vue'
import { whenever } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import Header from '~/components/ui/Header.vue'
import Layout from '~/components/ui/Layout.vue'
import Card from '~/components/ui/Card.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Section from '~/components/ui/Section.vue'
import Link from '~/components/ui/Link.vue'

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.Home.title')
}))

const store = useStore()
const logger = useLogger()
const nodeinfo = computed(() => store.state.instance.nodeinfo)

const podName = computed(() => get(nodeinfo.value, 'metadata.nodeName') || 'Funkwhale')
const banner = computed(() => get(nodeinfo.value, 'metadata.banner'))
const shortDescription = computed(() => get(nodeinfo.value, 'metadata.shortDescription'))
const longDescription = useMarkdown(() => get(nodeinfo.value, 'metadata.longDescription', ''))
const rules = computed(() => get(nodeinfo.value, 'metadata.rules'))
const contactEmail = computed(() => get(nodeinfo.value, 'metadata.contactEmail'))
const anonymousCanListen = computed(() => get(nodeinfo.value, 'metadata.library.anonymousCanListen'))
const openRegistrations = computed(() => get(nodeinfo.value, 'openRegistrations'))
const defaultUploadQuota = computed(() => get(nodeinfo.value, 'metadata.defaultUploadQuota'))

const stats = computed(() => {
  const users = get(nodeinfo.value, 'usage.users.activeMonth', 0)
  const hours = get(nodeinfo.value, 'metadata.library.music.hours', 0)

  if (users === null) {
    return null
  }

  return { users, hours }
})

const backgroundImage = computed(() =>
  banner.value
    ? `url(${store.getters['instance/absoluteUrl'](banner.value)})`
    : 'radial-gradient(circle at 80%, rgb(55, 122, 170), transparent), linear-gradient(135deg, rgb(40, 88, 125) 0%, rgb(64, 190, 220) 100%)'
)

// TODO (wvffle): Check if needed
const router = useRouter()
whenever(() => store.state.auth.authenticated, () => {
  logger.log('Authenticated, redirecting to /library…')
  router.push('/library')
})
</script>

<template>
  <Layout
    v-title="labels.title"
    stack
    main
  >
    <Header
      page-heading
      :class="$style.banner"
      :h1="t('components.Home.header.welcome', {podName: podName})"
    >
      <p :class="$style.description">
        {{ shortDescription }}
      </p>
      <div>
        <img
          :class="$style.logo"
          src="../assets/network.png"
          alt=""
        >
      </div>
      <Spacer />
      <Spacer />
      <Spacer />
      <Section
        align-left
        :columns-per-item="3"
        :h2="t('components.Home.header.about')"
      >
        <Layout
          flex
          :class="$style['long-description']"
        >
          <div>
            <p v-if="!longDescription">
              {{ t('components.Home.placeholder.noDescription') }}
            </p>
            <!-- TODO: Use new Ui elements once we can test with data -->
            <template v-if="longDescription || rules">
              <sanitized-html
                v-if="longDescription"
                id="renderedDescription"
                :html="longDescription"
              />
              <div
                v-if="longDescription"
                class="ui hidden divider"
              />
              <div class="ui relaxed list">
                <div
                  v-if="longDescription"
                  class="item"
                >
                  <i class="arrow right icon" />
                  <div class="content">
                    <router-link
                      class="ui link"
                      :to="{name: 'about'}"
                    >
                      {{ t('components.Home.link.learnMore') }}
                    </router-link>
                  </div>
                </div>
                <div
                  v-if="rules"
                  class="item"
                >
                  <i class="book open icon" />
                  <div class="content">
                    <router-link
                      v-if="rules"
                      class="ui link"
                      :to="{name: 'about', hash: '#rules'}"
                    >
                      {{ t('components.Home.link.rules') }}
                    </router-link>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </Layout>
        <Card
          v-if="stats"
          :title="t('components.Home.header.statistics')"
          caption
          style="--grid-column: -5 /-1;"
        >
          <div>
            <i class="bi bi-people-fill" />
            {{ t('components.Home.stat.activeUsers', stats.users) }}
          </div>
          <div>
            <i class="bi bi-music-note-list" />
            {{ t('components.Home.stat.hoursOfMusic', stats.hours) }}
          </div>
        </Card>
        <Card
          v-if="contactEmail"
          :title="t('components.Home.header.contact')"
          :to="`mailto:${contactEmail}`"
        >
          <p>
            <i class="bi bi-envelope-at-fill" />
            {{ contactEmail }}
          </p>
        </Card>
      </Section>
    </Header>

    <Section
      align-left
      :columns-per-item="3"
      style="row-gap: 64px;"
    >
      <Section
        :h2="t('components.Home.header.aboutFunkwhale')"
        :class="$style.about"
      >
        <div>
          <p>
            {{ t('components.Home.description.funkwhale.paragraph1') }}
          </p>
          <p>
            {{ t('components.Home.description.funkwhale.paragraph2') }}
          </p>
          <Link
            to="https://funkwhale.audio"
            icon="bi-box-arrow-up-right"
          >
            {{ t('components.Home.link.funkwhale') }}
          </Link>
        </div>
      </Section>
      <Section
        :h2="t('components.Home.header.signup')"
        :class="$style.signup"
      >
        <template v-if="openRegistrations">
          <p>
            {{ t('components.Home.description.signup') }}
          </p>
          <p v-if="defaultUploadQuota">
            {{ t('components.Home.description.quota', { quota: humanSize(defaultUploadQuota * 1000 * 1000) }) }}
          </p>
          <signup-form
            button-classes="success"
            :show-login="false"
          />
        </template>
        <div v-else>
          <p>
            {{ t('components.Home.help.registrationsClosed') }}
          </p>
          <Link
            to="https://funkwhale.audio/#get-started"
            icon="bi-box-arrow-up-right"
          >
            {{ t('components.Home.link.findOtherPod') }}
          </Link>
        </div>
      </Section>
      <login-form
        is-card
        primary
        solid
        :title="t('components.Home.header.login')"
        :class="$style.loginCard"
        button-classes="success"
        :show-signup="false"
      />
    </Section>

    <Section :h2="t('components.Home.header.links')">
      <Card
        v-if="anonymousCanListen"
        tiny
        :title="t('components.Home.link.publicContent.label')"
        icon="bi-headphones"
        to="/library"
      >
        <p>
          {{ t('components.Home.link.publicContent.description') }}
        </p>
      </Card>
      <Card
        :title="t('components.Home.link.mobileApps.label') "
        icon="bi-phone-fill large"
        to="https://funkwhale.audio/apps"
      >
        <p> {{ t('components.Home.link.mobileApps.description') }} </p>
      </Card>
      <Card
        :title=" t('components.Home.link.userGuides.label') "
        icon="bi-book-half large"
        to="https://docs.funkwhale.audio/user/index.html"
      >
        <p> {{ t('components.Home.link.userGuides.description') }} </p>
      </Card>
    </Section>
    <Section v-if="anonymousCanListen">
      <!-- TODO: Update design here. Cannot do it right now because `anonymousCanListen` is `undefined`-->
      <AlbumWidget
        :title="t('components.Home.header.newAlbums')"
        :query="{
          playable: true,
          ordering: ['-creation_date'],
          page_size: 10
        }"
      >
        <!-- TODO: Consider using Link component or Section action -->
        <router-link to="/library">
          {{ t('components.Home.link.viewMore') }}
          <div class="ui hidden divider" />
        </router-link>
      </AlbumWidget>
      <div class="ui hidden section divider" />
      <h3 class="ui header">
        {{ t('components.Home.header.newChannels') }}
      </h3>
      <ChannelsWidget
        :query="{
          content_category: 'music',
          ordering: ['-creation_date'],
          external: false,
          page_size: 10
        }"
        show-modification-date
      />
    </Section>
    <Spacer />
    <Spacer />
  </Layout>
</template>

<style module>

.banner {
  position: relative;

  color: white;
  text-shadow: .5px .5px 4px rgba(0, 0, 0, 0.5);

  --logo-width: min(60rem, max(63%, 350px));

  padding-top: calc(var(--logo-width) / 1.6 - 14rem);

  &::before{
      content: "";
      position: absolute;
      inset: -32px;
      background-repeat: no-repeat;
      background-size: cover;
      background-image: v-bind('backgroundImage');
  }

  > *{ z-index: 2; }

  .description {
    font-weight: 700;
    max-width: min(220px, calc(100% - var(--logo-width)));
    &:empty { display: none; }
  }
  :has(>.logo) {
      position: relative;
      > .logo {
        width: var(--logo-width);
        height: auto;
        position: absolute;
        bottom: -12rem;
        right: max(-32px, calc(5% - 7rem));
        z-index: -2;
      }
      z-index: -2;
  }
}
i {
    min-width: 24px;
    display: inline-block;
}

p {
    text-wrap: balance;
}

.about, .signup, .long-description {
    grid-column: 1 / -5 !important;
    margin-bottom: 58px;
}

.loginCard{
    grid-column: -5 / -1 !important;
    grid-row: 1 / 4 !important;
    margin-bottom: 58px;
}

@media (max-width: 768px) {
    .about, .signup, .description, .long-description  { grid-column: 1 / -1 !important; }
}

@media (min-width: 1280px) {
    .about {
        grid-column: 1 / 5 !important;
    }
    .signup {
        grid-column: 5 / -5 !important;
    }


}
</style>
