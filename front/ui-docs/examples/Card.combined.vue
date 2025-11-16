<script setup lang="ts">
import Card from "@ui/Card.vue"
import Alert from "@ui/Alert.vue"
import Link from "@ui/Link.vue"
import Button from "@ui/Button.vue"

const alert = ( message: string ) => window?.alert(message)
</script>

<template>
  <Layout article>
    <!-- #region snippet -->
    <Alert red>
      <Card
        full
        primary
        title="Linked card with interactive elements (confusing)"
        to="./card.md"
        :tags="['rock', 'folk', 'punk']"
        icon="bi-exclamation large"
      >
        <Button
          low-height
          :on-click="()=>alert('Button clicked')"
        >
          Click me!
        </Button>

        <Link
          to="./card.md"
          align-text="end"
        >
          Open this file in a new window
        </Link>
      </Card>
    </Alert>

    <Alert>
      <Card
        full
        title="Card with interactive elements (better)"
        :tags="['rock', 'folk', 'punk']"
        icon="bi-check-lg large"
      >
        <Button
          secondary
          low-height
          :on-click="()=>alert('Button clicked')"
        >
          Click me!
        </Button>

        <Link
          secondary
          to="./card.md"
          align-text="end"
        >
          Open this file in a new window
        </Link>
        <template #action>
          <Link
            solid
            grow
            primary
            to="./card.md"
            align-text="center"
          >
            Go!
          </Link>
        </template>
      </Card>
    </Alert>
    <!-- #endregion snippet -->
  </Layout>
</template>
