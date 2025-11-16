<script setup lang="ts">
import Layout from '@ui/Layout.vue'
import Table from '@ui/Table.vue'
import Button from '~/components/ui/Button.vue';
</script>

<template>
  <Layout
    article
    class="default"
  >
    <!-- #region snippet -->
    <Table
      is-table
      :grid-template-columns="['200px', '1fr', 'auto']"
    >
      <th>200px</th>
      <th>1fr</th>
      <th><Button>th</Button></th>
      <td><Button>cell 1</Button></td>
      <td>cell 2</td>
      <td>cell 3</td>
      <td><Button>cell 4</Button></td>
      <td><Button>cell 5</Button></td>
      <td><Button>cell 6</Button></td>
    </Table>
  <!-- #endregion snippet -->
  </Layout>
</template>
