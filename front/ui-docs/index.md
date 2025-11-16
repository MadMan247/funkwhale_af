<script setup lang="ts">
import Layout from '@ui/Layout.vue'
import Card from '@ui/Card.vue'
</script>

# Funkwhale design component library

## Plan

<Layout flex>
    <Card solid blue flat to="/designing-pages"
        title="Designing pages"
        min-content
    />
    <Card solid blue flat to="https://design.funkwhale.audio"
        icon="bi-box-arrow-up-right"
        title="UI designs" >
    Check out the design system on our Penpot.
    </Card>
</Layout>

## Use

<Layout flex>
    <Card solid yellow flat to='/using-components'
    title="Using components"
    min-content
    />
    <Card solid yellow flat to="/using-color"
    title="Adding Color"
    min-content
    />
    <Card solid yellow flat to="/using-width"
    title="Setting width and height"
    min-content
    />
    <Card solid yellow flat to="/using-alignment"
    title="Aligning elements"
    min-content
    />
</Layout>

## Maintain

<Layout flex>
    <Card solid purple flat to="/maintaining-accessibility"
        title="Keeping the UI components accessible"
        min-content
    />
</Layout>

## Contribute

- [Improve the component library](./contributing)
- [Found a bug? Report it here](https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/?sort=created_date&state=opened&label_name%5B%5D=Type%3A%3AUX%2FUI&first_page_size=20)

::: warning

vitepress loads some stylesheets on its own, so the styles you see here may differ from those in the funkwhale app or on the homepage and the blog.

You can find these stylesheets in the directory `front/node_modules/vitepress/dist/client/theme-default/styles/`.

:::
