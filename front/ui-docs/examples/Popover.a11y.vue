<script setup lang="ts">
import Popover from '@ui/Popover.vue'
import Layout from '@ui/Layout.vue'
import OptionsButton from '@ui/button/Options.vue'
import PopoverItem from '@ui/popover/PopoverItem.vue'
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Popover>
      <template #default="{ toggleOpen }">
        <OptionsButton @click="toggleOpen" />
      </template>
      <template #items>
        <PopoverItem
          autofocus
          @click="() => { }"
        >
          Do nothing
        </PopoverItem>
      </template>
    </Popover>
    <!-- #endregion snippet -->
  </Layout>
</template>
