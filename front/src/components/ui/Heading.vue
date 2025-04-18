<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  [H in `h${ '1' | '2' | '3' | '4' | '5' | '6' }`]? : string
} & {
  [S in 'page-heading' | 'section-heading' | 'large-section-heading' | 'subsection-heading' | 'caption' | 'title' | 'radio' | 'secondary' ]? : true
}>()

const [level, title] = Object.entries(props).find(([key, value]) => value && key.startsWith('h')) || ['h1', '']
const size = computed(() => (Object.entries(props).find(([key, value]) => value && key !== level)?.[0] || 'section-heading').replace('-', '').toLowerCase())
</script>

<template>
  <component
    :is="level"
    :class="[$style[size], $style.heading]"
  >
    <slot name="before" />
    {{ title }}
    <slot />
    <slot name="after" />
  </component>
</template>

<style module>
  /* Any heading */
  :is(h1, h2, h3, h4, h5, h6).heading { margin: 0; padding:0; vertical-align: baseline; align-self: baseline;}

  /* Page heading */
  :is(*, .vp-doc h3).pageheading { font-size: 36px; font-weight: 900; letter-spacing: -1px; }

  /* TODO: Decide on a size. All mockups on https://design.funkwhale.audio/ have 20px. */
  :is(*, .vp-doc h3).largesectionheading { font-size: 28px; font-weight: 700; letter-spacing: -.5px; }

  /* Section heading, Modal heading [DEFAULT] */
  :is(*, .vp-doc h3).sectionheading { font-size: 20px; font-weight: 700; letter-spacing: -.5px; }

  /* Form subsection */
  :is(*, .vp-doc h3).subsectionheading {font-size: 16px; font-weight: 600; letter-spacing: 0; }

  /* input caption */
  :is(*, .vp-doc h3).caption {font-size: 14px; font-weight: 600; letter-spacing: .25px; }

  /* Tab title, Channel title, Card title, Activity title */
  :is(*, .vp-doc h3).title { font-size: 16px; font-weight: 700; line-height: 18px; }

  /* Primary radio title */
  :is(*, .vp-doc h3).radio { font-size: 28px; font-weight: 900; letter-spacing: -.5px; }

  /* Secondary radio title */
  :is(*, .vp-doc h3).secondary { font-size: 28px; font-weight: 300; letter-spacing: -.5px; }
</style>
