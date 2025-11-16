<script setup lang="ts">
import Alert from "@ui/Alert.vue"
import Button from "@ui/Button.vue"
</script>

<template>
  <div
    class="funkwhale default"
    style="display: contents;"
  >
    <!-- #region snippet -->
    <Alert>
      Awesome artist
      <template #actions>
        <Button disabled>
          Deny
        </Button>
        <Button primary>
          Got it
        </Button>
      </template>
    </Alert>
    <!-- #endregion snippet -->
  </div>
</template>
