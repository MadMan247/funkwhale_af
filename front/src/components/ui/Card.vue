<script setup lang="ts">
import { computed, getCurrentInstance, useId } from 'vue'

import { type RouterLinkProps, RouterLink } from 'vue-router'
import { type ColorProps, type DefaultProps, type PastelProps, type RaisedProps, type VariantProps, color } from '~/composables/color'
import { type WidthProps, width } from '~/composables/width'

import Pill from '@ui/Pill.vue'
import Alert from '@ui/Alert.vue'
import { type Props as AlertProps } from '@ui/Alert.vue'
import Layout from '@ui/Layout.vue'
import Spacer from '@ui/Spacer.vue'

// #region props
const props = defineProps<{
  title: string
  category?: true | 'h1' | 'h2' | 'h3' | 'h4' | 'h5'

  tags?: string[]
  image?: string | { src: string, style?: 'withPadding', label?: string }
  icon?: string

  flat?: true

  alertProps?: AlertProps
} & Partial<RouterLinkProps>
  &(PastelProps | ColorProps | DefaultProps)
  & RaisedProps
  & VariantProps
  & WidthProps
  >()
// #endregion props

const titleId = `title-${useId()}`

const tags = computed(() => {
  // TODO: Do we want to display only 2 tags? I found this confusing... what's the purpose?
  return props.tags?.slice(0, 2)
})

const image = typeof props.image === 'string' ? { src: props.image } : props.image

const isExternalLink = computed(() => {
  return typeof props.to === 'string' && props.to.startsWith('http')
})

const hasClickEventListener = computed(
  () => !!getCurrentInstance()?.vnode.props?.onClick
);

const attributes = computed(() =>
  color(props, (props.to || hasClickEventListener.value) ? ['interactive', 'solid'] : [])(
    width(props, ['medium'])()
  ))
</script>

<template>
  <Layout
    stack
    no-gap
    :class="[{ [$style.card]: true, [$style['is-category']]: category===true }, 'card']"
    v-bind="{...attributes, ...$attrs, class: `${attributes.class} ${$attrs.class}`}"
  >
    <!-- Link -->

    <a
      v-if="props.to && isExternalLink"
      :class="$style.covering"
      :href="to?.toString()"
      :aria-labelledby="titleId"
      target="_blank"
    />
    <RouterLink
      v-if="props.to && !isExternalLink"
      :class="$style.covering"
      :to="props.to"
      :aria-labelledby="titleId"
    />

    <!-- Image -->

    <div
      v-if="$slots.image"
      :class="[$style.image, 'card-image']"
    >
      <slot
        name="image"
        :src="image"
      />
    </div>
    <img
      v-else-if="image"
      :src="image.src"
      :alt="image.label || ''"
      :title="image.label"
      :class="[{ [$style.image]: true, [$style['with-padding']]: image.style === 'withPadding' }, 'card-image']"
    >
    <Spacer
      v-else
      :size="'small' in props ? 20 : 28"
    />

    <!-- Icon -->

    <i
      v-if="props.icon"
      :class="[$style.icon, 'bi', icon]"
      role="img"
      :aria-label="`${props.icon.replace('bi-', '').replace('-lg', '')} icon`"
    />

    <!-- Title -->

    <!-- TODO: Use new `Heading` component instead! -->
    <component
      :is="typeof category === 'string' ? category : 'h6'"
      :id="titleId"
      :class="$style.title"
    >
      {{ title }}
    </component>

    <!-- Topright action -->

    <div
      v-if="$slots.topright"
      :class="$style.topright"
    >
      <slot name="topright" />
    </div>

    <!-- Content -->

    <Alert
      v-if="$slots.alert"
      v-bind="alertProps"
      :class="$style.alert"
    >
      <!-- TODO: Place `alertProps` into slot props :-) -->
      <slot name="alert" />
    </Alert>

    <Layout
      v-if="tags"
      flex
      gap-4
      :class="$style.tags"
    >
      <Pill
        v-for="(tag, index) in tags"
        :key="index"
      >
        {{ tag }}
      </Pill>
    </Layout>

    <Layout
      v-if="$slots.default"
      :no-gap="Object.entries($attrs).every(
        ([key, value]) => !key.startsWith('gap'))"
      :class="$style.content"
    >
      <slot />
    </Layout>

    <Spacer
      grow
      no-size
    />

    <!-- Footer and Action -->

    <div
      v-if="$slots.footer"
      :class="$style.footer"
    >
      <slot name="footer" />
    </div>

    <div
      v-if="$slots.action"
      :class="$style.action"
    >
      <slot name="action" />
    </div>

    <Spacer
      v-if="!$slots.footer && !$slots.action"
      :size="'small' in props && props.small? 18 : 24"
    />
  </Layout>
</template>

<style module lang="scss">
.card {
  --fw-card-padding: v-bind("'small' in props && props.small ? '16px' : '24px'");

  position: relative;

  cursor: v-bind("hasClickEventListener ? 'pointer' : 'default'");

  color: var(--fw-text-color);
  background-color: var(--fw-bg-color);
  box-shadow: 0px 2px 8px 0px v-bind("flat?'transparent':'var(--shadow-color)'");

  border-radius: var(--fw-border-radius);
  font-size: 1rem;

  >.covering {
    position: absolute;
    inset: 0;

    &~:is(.title, .content:not(:has(:is(button, input, a, select)))) {
      pointer-events:none;
    }
    &:hover~:is(.content:not(:has(:is(button, input, a, select)))) {
      text-decoration: underline
    }
  }

  >.image {
    overflow: hidden;
    border-radius: var(--fw-border-radius) var(--fw-border-radius) 0 0;
    object-fit: cover;
    width: 100%;
    aspect-ratio: 1;
    position:relative;
    pointer-events: none;

    &.with-padding {
      margin: var(--fw-card-padding) var(--fw-card-padding) calc(var(--fw-card-padding) / 2) var(--fw-card-padding);
      width: calc(100% - 2 * var(--fw-card-padding));
      border-radius: var(--fw-border-radius);
    }
  }

  >.icon {
    position: absolute;
    top: 20px;
    right: 20px;

    font-size: 1rem;

    pointer-events: none;

    &:global(.large) {
      font-size: 32px;
      margin: -8px;
    }
  }
  &:has(>.image)>.icon {
    top: var(--fw-card-padding);
    right: var(--fw-card-padding);

    font-size: 1.2rem;
  }

  >.title {
    margin: 0;
    padding: 0 var(--fw-card-padding);
    line-height: 1.3em;
    font-size: 1.125em;
    font-weight: bold;

    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    flex-shrink: 0;
  }
  &:has(>.icon):not(:has(.image))>.title {
    padding-right:calc(var(--fw-card-padding) + 22px);
  }
  &.is-category>.title {
    font-size: 1.75em;
    padding-bottom: .125em;
  }
  &:has(>.image:not(.with-padding))>.title {
    margin-top:16px;
  }

  >.topright {
    position: absolute;
    top: 0;
    right: 0;
  }

  >.alert {
    padding-left: var(--fw-card-padding);
    padding-right: var(--fw-card-padding);
    margin-top: 8px;
  }

  >.tags {
    padding: 0 var(--fw-card-padding);
    margin: 8px  -4px 0px -4px;
  }

  >.content {
    overflow: hidden;
    padding: 0 var(--fw-card-padding);
    /* Consider making all line height, vertical paddings, margins and borders,
    a multiple of a global vertical rhythm so that side-by-side lines coincide */
    line-height: 24px;
    margin-top: 8px;
  }

  >.footer {
    padding: calc(var(--fw-card-padding) - 4px);
    display: flex;
    gap: 4px;
    align-items: end;
    font-size: 0.8125rem;
    margin-top: 16px;

    >.options-button {
      margin-left: auto;
    }
  }

  /* If both card and an action control has a special color, draw foreground color line above that action control */
  &:global(:is(.primary, .destructive)) > .action :global(:is(.primary, .destructive)) {
      border-top-color: color-mix(in oklab, var(--color) 50%, transparent) !important;
  }

  >.action {
    display: flex;
    background: color-mix(in oklab, var(--fw-bg-color) 80%, var(--fw-gray-500));
    border-bottom-left-radius: var(--fw-border-radius);
    border-bottom-right-radius: var(--fw-border-radius);
    margin-top: var(--fw-card-padding);

    >*:not(.with-padding) {
      margin: 0;
      border-top-left-radius: 0;
      border-top-right-radius: 0;
      border: 8px solid transparent;
      &:not(:first-child) {
        border-bottom-left-radius: 0;
      }
      &:not(:last-child) {
        border-bottom-right-radius: 0;
      }
    }
  }
}
</style>
