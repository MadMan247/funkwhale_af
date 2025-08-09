<script setup>
import '~/style/funkwhale.scss'
import DefaultTheme from 'vitepress/theme'
const { Theme } = DefaultTheme
</script>

<template>
  <Theme>
    <template>
    </template>
  </Theme>
</template>

<style>
:root {
  --vp-sidebar-width: 250px;
}

.Layout {
  --vp-c-text-1: color-mix(in oklab, light-dark(var(--fw-gray-970), var(--fw-beige-100)) 100%, transparent);
  --vp-c-text-2: color-mix(in oklab, light-dark(var(--fw-gray-970), var(--fw-beige-100)) 60%, transparent);

  --vp-c-bg: color-mix(in oklab, light-dark(white, var(--fw-gray-950)) 50%, transparent);
  --vp-c-bg-soft: color-mix(in oklab, light-dark(var(--fw-beige-300), var(--fw-gray-970)) 50%, transparent);

  --vp-c-gutter: light-dark(transparent, var(--fw-gray-970));
  --vp-local-nav-bg-color: light-dark(transparent, var(--fw-gray-970));
  --vp-code-block-bg: light-dark(var(--fw-beige-200), var(--fw-gray-900));
  --vp-c-bg-alt: light-dark(var(--fw-beige-300), var(--fw-gray-850));
  --vp-c-divider: light-dark(var(--fw-beige-300), var(--fw-gray-850));
  --vp-code-line-highlight-color: light-dark(var(--fw-beige-300), var(--fw-gray-850));
  --vp-custom-block-details-bg: light-dark(var(--fw-beige-400), var(--fw-gray-800));
  --vp-nav-bg-color: light-dark(var(--fw-beige-100), var(--fw-gray-960));
  --vp-sidebar-bg-color: light-dark(var(--fw-beige-100), var(--fw-gray-960));
  background-color: light-dark(var(--fw-beige-100), var(--fw-gray-960));
}

.VPNavBarTitle .title {
  font-size: 14px;
}

.vp-doc div[class*="language-"]:has(+h1) {
  width: min-content;
  float: right;
  margin: -4px -32px -4px -4px;
  background: transparent;

  &>pre {
    padding-right: 32px;
  }
}

.language-template:has(~.preview) {
  flex-grow: 1;

  &~.preview {
    flex-grow: 0;
  }
}

:has(.vp-doc) .container .items {
  background: light-dark(var(--fw-beige-100), var(--fw-gray-960));
}

.vp-doc .custom-block {
  margin-left: -2px;

  /* background-color: transparent; */
  border-width: 0;
  border-radius: 0;
  border-left-width: 4px;

  --vp-custom-block-details-border: currentcolor;

  &:has(summary:hover) {
    color: var(--fw-blue-400)
  }

  --vp-custom-block-details-bg: color-mix(in oklab, var(--vp-custom-block-details-border) 0%, transparent);
  --vp-custom-block-warning-border: var(--fw-pastel-yellow-4);
  --vp-custom-block-warning-bg: color-mix(in oklab, var(--vp-custom-block-warning-border) 10%, transparent);
  --vp-custom-block-info-border: var(--fw-pastel-blue-4);
  --vp-custom-block-info-bg: color-mix(in oklab, var(--vp-custom-block-info-border) 10%, transparent);
}

.funkwhale h3 {
  /* override vitepress */
  margin: 0;
}

.vp-doc .preview:not(.funkwhale .preview) {
  padding: 16px 0;
  flex-grow: 1;
  border-radius: 8px;
  justify-content: start;
  --vp-code-block-bg: transparent;

  &:not(.transparent) {
    background-color: var(--background-color);
    box-shadow: 0px 0px 16px 16px var(--background-color);
    margin: 16px 0;
    padding: 0;

  }

  /* .preview overrides the cascade coming from .vp-docs and other containers
  that may leak rules here */
  p {
    margin: 0;
    line-height: normal
  }
}
</style>
