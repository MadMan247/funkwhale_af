---
layout: page
---

<script setup lang="ts">
import { ref } from 'vue'

import Nav from '@ui/Nav.vue'
import NavA11y from '@/examples/Nav.a11y.vue'

const nav = ref([{ title: 'Go up', to: '../' }, { title: 'Home', to: './', badge: "2" }])
</script>

```ts
import Nav from "@ui/Nav.vue"
```

# Nav

A group of links (such as a table of contents or a navigation bar) or tabs.

You can add a `badge` or an `icon` to each tab link.

## Tabs

Choose a unique `tabQueryField` to enable tabbing functionality. It allows users to reload or share the page without losing the active tab state. See the example below to learn how to make your tabbed interfaces accessible.

## Add a badge to a tab or link

A badge strongly urges the user to take a destructive or maintenance action. Only use when all of the following criteria are met:

1. A maintenance problem **calls for immediate action**
2. The button or link is **the fastest way to get there**
3. The user needs to take a maintenance action to **make the badge disappear**

Typical example include:

- A message inboxes where the primary feature is reading and archiving messages (in Funkwhale: User messages)
- A moderation feature where reports need to be answered

::: tip Using this component

## A11y Checklist

- [ ] Navigation links have sufficient contrast (4.5:1) against their background. Select different color props if needed. [1.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-3)
- [ ] Focus indicators have sufficient contrast (3:1). Select different color props if needed. [1.4.11](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-11)
- [ ] Navigation links have clear, descriptive text that indicates their destination. [2.4.4](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-4)
- [ ] User can go multiple ways (Search, URL input, Links...) to find relevant pages. [2.4.5](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-5); [Deep dive: Multiple ways](https://www.w3.org/WAI/WCAG22/Understanding/multiple-ways.html)

## Accessible Nav

<NavA11y />

<<<@/examples/Nav.a11y.vue#model{ts}

<<<@/examples/Nav.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#nav)

:::
