<script setup lang="ts">


defineProps<{
  backgroundImage: string;
  title: string;
  overflowing?: true
  icon?: string
}>();
</script>

<template>
  <section
    :class="[$style.banner, overflowing && $style.overflowing]"
  >
    <h1>
      <template v-if="icon">
        <i :class="`bi ${icon}`" />&nbsp;
      </template>
      {{ title }}
    </h1>
  </section>
</template>

<style module>

    .banner {
      position: relative;
      height: 202px;

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

      > h1 {
          position: absolute;
            bottom: 24px;
            left: 16px;
      }

      &.overflowing {
          background-image: v-bind('backgroundImage');
      }
    }
</style>
