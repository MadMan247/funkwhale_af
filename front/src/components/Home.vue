<script setup lang="ts">
import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import useLogger from '~/composables/useLogger'
import { useStore } from '~/store'
import { whenever } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()

const store = useStore()
const logger = useLogger()

// TODO (wvffle): Check if needed
const router = useRouter()
whenever(() => store.state.auth.authenticated, () => {
  logger.log('Authenticated, redirecting to /library…')
  router.push('/library')
})
router.push('/channels/acid_fog')
</script>

<template>
  <div>
    <img
      :class="$style.logo"
      src="../assets/network.png"
      alt=""
    >
  </div>
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
      background-color: gray;
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
