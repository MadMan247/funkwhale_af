<script setup lang="ts">
import Toc from '~/components/ui/Toc.vue'
import Section from '~/components/ui/Section.vue'
import Spacer from '~/components/ui/Spacer.vue'
</script>

```ts
import Toc from "~/components/ui/Toc.vue"
```

# Table of Contents

The table of contents component renders a navigation bar on the right of the screen. Users can click on the items in the contents bar to skip to specific headers.

| Prop      | Data type      | Required? | Description                                         |
| --------- | -------------- | --------- | --------------------------------------------------- |
| `heading` | Enum\<String\> | No        | The heading level rendered in the table of contents |

::: details Supported headings

- `h1`
- `h2`
- `h3`
- `h4`
- `h5`
- `h6`

:::

## Default

By default table of contents only renders `<h1>` tags

```vue-html
<Toc>
  <h1>This is a Table of Contents</h1>
  Content...

  <h1>It automatically generates from headings</h1>
  More content...
</Toc>
```

<ClientOnly>
  <Toc>
    <h1>This is a Table of Contents</h1>
    <p>
      In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
    </p>
    <p>
      Unde praesentium voluptates esse in placeat. Quis qui sint illo tempore omnis sed. Ab dicta omnis aut dolor voluptate maxime repudiandae ea. Aspernatur alias et architecto asperiores in. A sunt necessitatibus voluptatem veniam at dolore. Dolorum saepe est eveniet dignissimos laborum.
    </p>
    <p>
      Qui impedit dicta earum. Qui repudiandae est magnam. Illum sit ratione exercitationem fugiat aut tempore. Ut sit deserunt ratione ut architecto deleniti ea magnam. Voluptatibus dignissimos voluptatem rem fugiat.
    </p>
    <h1>It automatically generates from headings</h1>
    <p>
      In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
    </p>
    <h1>Heading h1 - A</h1>
    <p>
      Unde praesentium voluptates esse in placeat. Quis qui sint illo tempore omnis sed. Ab dicta omnis aut dolor voluptate maxime repudiandae ea. Aspernatur alias et architecto asperiores in. A sunt necessitatibus voluptatem veniam at dolore. Dolorum saepe est eveniet dignissimos laborum.
    </p>
    <h1>Heading h1 - B</h1>
    <p>
      Qui impedit dicta earum. Qui repudiandae est magnam. Illum sit ratione exercitationem fugiat aut tempore. Ut sit deserunt ratione ut architecto deleniti ea magnam. Voluptatibus dignissimos voluptatem rem fugiat.
    </p>
    <h2>Heading h2 - C</h2>
    <p>
      In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
    </p>
    <h1>Heading h1 - D</h1>
    <p>
      In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
    </p>
  </Toc>
</ClientOnly>

## Custom headings

You can specify the heading level you want to render in the table of contents by passing it to the `heading` prop.

```vue-html{2}
<Toc
  heading="h3"
>
  <h1>This is a Table of Contents</h1>
  Content...

  <h2>It automatically generates from headings</h2>
  More content...

  <Section h3="Radios">
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  </Section>
  <Section h3="Artists">
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  </Section>
  <Section h3="Albums">
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  </Section>
</Toc>
```

<ClientOnly>
<Toc
  heading="h3"
>
  <h1>This is a Table of Contents</h1>
  Content...

  <h2>It automatically generates from headings</h2>
  More content...

  <Spacer size-64/>
  <Section h3="Radios">
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  </Section>
  <Spacer size-64/>
  <Section h3="Artists">
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  </Section>
  <Spacer size-64/>
  <Section h3="Albums">
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  <p>
    In expedita ratione consequatur rerum et ullam architecto. Qui ut doloremque laboriosam perferendis corporis voluptatibus voluptates. Ad ducimus adipisci vitae mollitia quis. Aut placeat quaerat maxime velit et eius voluptas fugit. Omnis et et perspiciatis mollitia occaecati.
  </p>
  </Section>
</Toc>
</ClientOnly>
