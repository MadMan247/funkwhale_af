<script setup lang="ts">
import { computed } from 'vue'
import { char, createRegExp, exactly, global, oneOrMore, word } from 'magic-regexp/further-magic'
import showdown from 'showdown'

import SanitizedHtml from './SanitizedHtml.vue'

interface Props {
  md: string
}

const props = defineProps<Props>()

showdown.extension('openExternalInNewTab', {
  type: 'output',
  regex: createRegExp(
    exactly('<a'),
    char.times.any(),
    exactly(' href="'),
    oneOrMore(
      // TODO: Use negative set when implemented: https://github.com/danielroe/magic-regexp/issues/237#issuecomment-1606056174
      char
    ),
    exactly('">'),
    [global]
  ),
  replace (text: string) {
    const href = createRegExp(
      exactly('href="'),
      oneOrMore(
        // TODO: Use negative set when implemented: https://github.com/danielroe/magic-regexp/issues/237#issuecomment-1606056174
        char
      ).as('url'),
      exactly('">')
    )

    const matches = text.match(href)
    const url = matches?.groups?.url ?? './'

    if ((!url.startsWith('http://') && !url.startsWith('https://')) || url.startsWith('mailto:')) {
      return text
    }

    try {
      const { hostname } = new URL(url)
      return hostname !== location.hostname
        ? text.replace(href, `href="${url}" target="_blank" rel="noopener noreferrer">`)
        : text
    } catch {
      return text.replace(href, `href="${url}" target="_blank" rel="noopener noreferrer">`)
    }
  }
})

showdown.extension('linkifyTags', {
  type: 'language',
  regex: createRegExp(
    exactly('#'),
    oneOrMore(word),
    [global]
  ),
  // regex: /#[^\W]+/g,
  replace (text: string) {
    return `<a href="/library/tags/${text.slice(1)}">${text}</a>`
  }
})

const markdown = new showdown.Converter({
  extensions: ['openExternalInNewTab', 'linkifyTags'],
  ghMentions: true,
  ghMentionsLink: '/@{u}',
  simplifiedAutoLink: true,
  openLinksInNewWindow: false,
  simpleLineBreaks: true,
  strikethrough: true,
  tables: true,
  tasklists: true,
  underline: true,
  noHeaderId: true,
  headerLevelStart: 3,
  literalMidWordUnderscores: true,
  excludeTrailingPunctuationFromURLs: true,
  encodeEmails: true,
  emoji: true
})

const html = computed(() => markdown.makeHtml(props.md))
</script>

<template>
  <SanitizedHtml :html="html" />
</template>
