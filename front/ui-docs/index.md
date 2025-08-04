<script setup lang="ts">
import Layout from '../src/components/ui/Layout.vue'
import Card from '../src/components/ui/Card.vue'
</script>

# Funkwhale design component library

## Plan

<Layout flex>
    <Card default raised to="/designing-pages"
        title="Designing pages"
        min-content
    />
    <Card default raised to="https://design.funkwhale.audio"
        title="UI designs" >
    Check out the design system on our Penpot.
    </Card>
</Layout>

## Use

<Layout flex>
    <Card default raised to='/using-components'
    title="Using components"
    min-content
    />
    <Card default raised to="/using-color"
    title="Adding Color"
    min-content
    />
    <Card default raised to="/using-width"
    title="Setting width and height"
    min-content
    />
    <Card default raised to="/using-alignment"
    title="Aligning elements"
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
