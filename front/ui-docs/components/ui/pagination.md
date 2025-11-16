---
layout: page
---

<script setup lang="ts">
import { ref } from 'vue'

import Pagination from "@ui/Pagination.vue"

import PaginationA11y from "@/examples/Pagination.a11y.vue"

const page = ref(1)
</script>

```ts
import Pagination from "@ui/Pagination.vue"
```

# Pagination

The pagination component helps users navigate through large lists of results by splitting them up into pages.

| Prop           | Data type | Required? | Description                            |
| -------------- | --------- | --------- | -------------------------------------- |
| `pages`        | Number    | Yes       | The total number of pages to paginate. |
| `v-model:page` | Number    | Yes       | The page number of the current page.   |

> [!Note]
> Use this component for navigation targets only. [The semantics of the `<nav>` element apply](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/nav#usage_notes).

## Pagination model

Create a pagination bar by passing the number of pages to the `pages` prop. Use `v-model` to sync the selected page to your page data. Users can click on each button or input a specific page and hit `return`.

```vue-html
<Pagination :pages="8" v-model:page="page" />
```

<Pagination :pages="9" v-model:page="page" />

::: tip Using this component

## A11y Checklist

- [ ] It's clear and obvious which section of the page the pagination control belongs to. For example, the Pagination is directly below a paginated list of search results. [1.3.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-3-1)
- [ ] Page changes do not trigger unexpected context changes (like auto-scrolling to the top). [3.2.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-2-2)
- [ ] Users can locate content through multiple ways (e.g., pagination alongside search or filtering). [2.4.5](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-5)
- [ ] Users can determine their current location within the paginated content. [2.4.8](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-8)
- [ ] If the page content changes, a status message announces the update (e.g., "Showing results 11-20 of 45"). [4.1.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#4-1-3)

## Accessible Pagination

<PaginationA11y />

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#pagination)

:::
