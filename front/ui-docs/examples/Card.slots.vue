<script setup lang="ts">
import Card from "@ui/Card.vue"
import Button from '@ui/Button.vue'
import OptionsButton from '@ui/button/Options.vue'
import Spacer from '@ui/Spacer.vue'
import Layout from '@ui/Layout.vue'

const alert = ( message: string ) => window?.alert(message)
</script>

<template>
  <Layout
    article
    flex
  >
    <!-- #region snippet -->
    <Card title="Topright action">
      Contextual actions go to the top-right of the Card.
      <template #topright>
        <OptionsButton square-small />
      </template>
    </Card>

    <Card
      medium
      title="Footer"
    >
      Items in the footer region are secondary and will be displayed smaller than the main content.
      <template #footer>
        <Button
          outline
          icon="bi-upload"
          @click="alert('Uploaded. Press OK!')"
        >
          Upload
        </Button>
        <Spacer style="flex-grow: 1" />
        <OptionsButton />
      </template>
    </Card>

    <Card
      medium
      title="Call-to-Action"
    >
      Large Buttons or links at the bottom edge of the card serve as Call-to-Actions (CTA).
      <template #action>
        <Button
          secondary
          grow
          @click="alert('Open the pod picker')"
        >
          Action!
        </Button>
      </template>
    </Card>

    <Card
      full
      title="Multiple actions"
    >
      If there are multiple actions, they will be presented in a row.
      <template #action>
        <Button
          secondary
          ghost
          min-content
          align-text="start"
          icon="bi-chevron-left"
        >
          Items
        </Button>
        <Spacer
          h
          grow
        />
        <Button
          primary
          @click="alert('Yay')"
        >
          OK
        </Button>
        <Button
          destructive
          @click="alert('Yay')"
        >
          Cancel
        </Button>
      </template>
    </Card>
    <!-- #endregion snippet -->
  </Layout>
</template>
