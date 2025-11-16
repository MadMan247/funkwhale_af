<script setup lang="ts">
import { ref , computed} from "vue"

import Input from "@ui/Input.vue"
import Layout from "@ui/Layout.vue"
import Button from "@ui/Button.vue"
import Toggle from "@ui/Toggle.vue"
import Textarea from '@ui/Textarea.vue'
import Alert from '@ui/Alert.vue'
import Slider from "@ui/Slider.vue"
import Select from "@ui/Select.vue"
import Pills from "@ui/Pills.vue"

// #region model
const text = ref("")
const toggled = ref(false)
const username = ref("")
const password = ref("")
const options = {
  required: "We will not send you any E-Mails unless legally required",
  'important only': "You will be informed about important changes only",
  everything: "You will receive updates about every change"
} as const

const option = ref<keyof typeof options>('required')

const roles = ref({
  1: 'Maintainer',
  2: 'Contributor',
  3: 'User'
} as const)

const role = ref<keyof typeof roles.value>(2)

  const pills = ref < {
    currents: { type: 'custom' | 'preset', label: string }[],
    others?: { type: 'custom' | 'preset', label: string }[]
  }>({
    currents: [{
      type: 'preset',
      label: "Tag-A"
    }, {
      type: 'custom',
      label: "Tag-B"
    }, {
      type: 'custom',
      label: "Tag-C"
    }],
  others: []
  })

const errors = computed(()=>
  text.value.includes(' ')
  ? [ 'Make sure your message does not contain any spaces' ]
  : []
)
// #endregion model
</script>

<template>
  <Layout
    article
    class="solid default"
  >
    <!-- #region snippet -->
    <Layout
      stack
      class="outline"
      style="overflow: scroll; height: 83px; border-radius: 8px;"
    >
      <Alert
        v-for="(error, index) in errors"
        :key="error"
        red
      >
        Error {{ index+1 }} / {{ errors.length }}: {{ error }}
      </Alert>
    </Layout>
    <Layout
      form
      stack
      gap-48
    >
      <!-- #region textarea -->
      <Textarea
        v-model="text"
        label="Your message"
      />
      <!-- #endregion textarea -->

      <!-- #region pills -->
      <Pills
        :get="p => { pills = p }"
        :set="_ => pills"
      />
      <!-- #endregion pills -->

      <!-- #region select -->
      <Select
        v-model:current="role"
        v-model:options="roles"
        label="Select a role"
      />
      <!-- #endregion select -->

      <!-- #region toggle -->
      <Toggle
        v-model="toggled"
        label="Enable plugins"
      />
      <!-- #endregion toggle -->

      <!-- #region input -->
      <Input
        v-model="username"
        label="User name"
        autocomplete="username"
      />
      <Input
        v-model="password"
        label="Password"
        password
      />
      <!-- #endregion input -->

      <!--#region slider -->
      <Slider
        v-model="option"
        :options
        label="Receive E-Mails"
      />
      <!-- #endregion slider -->

      <Button primary>
        Submit
      </Button>
    </Layout>
    <!-- #endregion snippet -->
  </Layout>
</template>
