<script setup lang="ts">
import { computed, ref } from 'vue'

import { type Track, type User } from '~/types'

import Card from '~/components/ui/Card.vue'
import Layout from '~/components/ui/Layout.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Button from '~/components/ui/Button.vue'
import Activity from '~/components/ui/Activity.vue'
import Section from '~/components/ui/Section.vue'

const alignLeft = ref(false)

const attributes = computed(() => ({
  style: alignLeft.value ? 'justify-content: start' : ''
}))
</script>

# Navigation

When most of the screen changes, users perceive it as a page navigation. They will expect the "back" button to bring them to the precious screen. In addition, they may expect the URL to contain the current page for sharing.

This makes a component a "page". In this sense, modals are pages.

Not everything we want to share with the Url replaces most of the screen. What about switching a filter?
