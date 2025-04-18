<script setup lang="ts">
import type { BackendError } from '~/types'

import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'

import axios from 'axios'

import DomainsTable from '~/components/manage/moderation/DomainsTable.vue'

import Layout from '~/components/ui/Layout.vue'
import Spacer from '~/components/ui/Spacer.vue'
import Header from '~/components/ui/Header.vue'
import Toggle from '~/components/ui/Toggle.vue'
import Button from '~/components/ui/Button.vue'
import Input from '~/components/ui/Input.vue'
import Alert from '~/components/ui/Alert.vue'

interface Props {
  allowListEnabled: boolean
}

const props = defineProps<Props>()

const { t } = useI18n()

const router = useRouter()

const labels = computed(() => ({
  domains: t('views.admin.moderation.DomainsList.title')
}))

const domainName = ref('')
const domainAllowed = ref(props.allowListEnabled || undefined)

const isCreating = ref(false)
const errors = ref([] as string[])
const createDomain = async () => {
  isCreating.value = true
  errors.value = []

  try {
    const response = await axios.post('manage/federation/domains/', { name: domainName.value, allowed: domainAllowed.value })
    router.push({
      name: 'manage.moderation.domains.detail',
      params: { id: response.data.name }
    })
  } catch (error) {
    errors.value = (error as BackendError).backendErrors
  }

  isCreating.value = false
}
</script>

<template>
  <main v-title="labels.domains">
    <Layout
      form
      @submit.prevent="createDomain"
    >
      <Header
        page-heading
        :h1="t('views.admin.moderation.DomainsList.header.domains')"
      />
      <Alert
        v-if="errors && errors.length > 0"
        red
      >
        <h4 class="header">
          {{ t('views.admin.moderation.DomainsList.header.failure') }}
        </h4>
        <ul class="list">
          <li
            v-for="(error, key) in errors"
            :key="key"
          >
            {{ error }}
          </li>
        </ul>
      </Alert>
      <div class="field">
        <Input
          id="add-domain"
          v-model="domainName"
          type="text"
          name="domain"
          :label="t('views.admin.moderation.DomainsList.label.addDomain')"
        >
          <template #input-right>
            <Button
              primary
              :class="[{'loading': isCreating}, 'success']"
              type="submit"
              :disabled="isCreating"
            >
              {{ t('views.admin.moderation.DomainsList.button.add') }}
            </Button>
          </template>
        </Input>
        <div
          v-if="allowListEnabled"
        >
          <Toggle
            id="allowed"
            v-model="domainAllowed"
            name="allowed"
            :label="t('views.admin.moderation.DomainsList.label.addToAllowList')"
          />
        </div>
      </div>
    </Layout>
    <Spacer />
    <domains-table :allow-list-enabled="allowListEnabled" />
  </main>
</template>
