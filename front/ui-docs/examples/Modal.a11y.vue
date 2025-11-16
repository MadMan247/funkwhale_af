<script setup lang="ts">
import { ref } from 'vue'
import Alert from '@ui/Alert.vue'
import Button from '@ui/Button.vue'
import Modal from '@ui/Modal.vue'
import Layout from '@ui/Layout.vue'

const isStep1Open = ref(false)
const isStep2Open = ref(false)
const isStep3Open = ref(false)

function openModal() {
  isStep1Open.value = true
  isStep2Open.value = false
  isStep3Open.value = false
}
</script>

<template>
  <Layout article>
    <Button
      primary
      @click="openModal"
    >
      Publish album
    </Button>

    <Modal
      v-model="isStep1Open"
      title="Step 1 of 3: Add cover art"
    >
      <p>Every great album needs great cover art.</p>
      <img
        src="https://source.unsplash.com/random/400x200?music"
        alt="A randomly selected, music-related image from Unsplash."
        class="rounded"
      >
      <template #actions>
        <Button @click="isStep1Open = false">
          Cancel
        </Button>
        <Button
          primary
          autofocus
          @click="
            isStep1Open = false;
            isStep2Open = true;
          "
        >
          Save and continue
        </Button>
      </template>
    </Modal>

    <Modal
      v-model="isStep2Open"
      title="Step 2 of 3: Review details"
    >
      <p>Please confirm the album details before publishing.</p>
      <ul>
        <li><strong>Artist:</strong> The Funkwhales</li>
        <li><strong>Album:</strong> Cetacean Ops</li>
        <li><strong>Release Date:</strong> 2024</li>
      </ul>
      <template #actions>
        <Button
          @click="
            isStep2Open = false;
            isStep1Open = true;
          "
        >
          Back to cover art
        </Button>
        <Button
          primary
          autofocus
          @click="
            isStep2Open = false;
            isStep3Open = true;
          "
        >
          Continue to final step
        </Button>
      </template>
    </Modal>

    <Modal
      v-model="isStep3Open"
      title="Step 3 of 3: Confirm publication?"
      destructive
    >
      <template #alert>
        <Alert red>
          Publishing the album will make it publicly visible. This action cannot be
          undone through this interface.
        </Alert>
      </template>
      <p>Are you sure you want to publish "Cetacean Ops"?</p>
      <template #actions>
        <Button
          autofocus
          @click="isStep3Open = false"
        >
          Do not publish
        </Button>
        <Button
          destructive
          @click="isStep3Open = false"
        >
          Yes, publish album
        </Button>
      </template>
    </Modal>
  </Layout>
</template>
