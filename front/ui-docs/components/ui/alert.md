---
layout: page
---

<script setup>
import Alert from "@ui/Alert.vue"
import Button from "@ui/Button.vue"
import Layout from "@ui/Layout.vue"

import AlertColors from '@/examples/Alert.colors.vue'
import AlertActions from '@/examples/Alert.actions.vue'
import AlertAlly from '@/examples/Alert.a11y.vue'
</script>

```ts
import Alert from "@ui/Alert.vue"
```

# Alert

Display informative messages that may change and update over time

<<<@/../src/components/ui/Alert.vue#props{ts}

## Choose a role

By default, screenreaders will read out all alerts on a page. This is annoying and intrusive. Do use a more polite `role` such as `status` to skip the initial announcement, and use the (default) `alert` role only on extremely important announcements.

::: warning Careful with the `alert` role!

> The `alert` role is intended for messages that are dynamically displayed, not for content that appears on page load. For example, it can show an error message if user-added content has an invalid format or the backend throws an error - the alert would immediately read out the message. It should not be used on HTML that the user hasn't interacted with. For example, if a page loads with multiple visible alerts scattered throughout, choose a role other than `alert`, as the messages were not dynamically triggered.

[A11y Checklist](#a11y-checklist)

[The `role` attribute [MDN]](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/alert_role)

:::

## Align content

Read more: [Using Alignment props](/using-alignment)

## Add actions

<AlertActions />

<<<@/examples/Alert.actions.vue#snippet{vue-html 3-6}

## Apply color

::: warning Never rely on color alone to convey relevant information

Many people will not perceive certain colors, so give them other affordances to understand the meaning of a given alert.

Read more: [Using Color](/using-color)

:::

<Layout article grid="auto / repeat(auto-fit, minmax(max-content, 200px))">
  <AlertColors />
</Layout>

<<<@/examples/Alert.colors.vue#snippet{vue-html}

::: tip Using this component

## A11y Checklist

- [ ] Choose [the appropriate role](#choose-a-role). Use 'status' for non-urgent updates, 'alert' for important time-sensitive information. [4.1.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#4-1-2)
- [ ] Content is clear and concise. The first few words should convey the key message for screen reader users. [4.1.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#4-1-3)
- [ ] Text has sufficient contrast (4.5:1) against the alert's background color. [1.4.3](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-3)
- [ ] If the alert contains an action button, the button's purpose is conveyed by its label. [2.4.6](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-4-6)

## Accessible alert

<AlertA11y />

<<<@/examples/Alert.a11y.vue#snippet{vue-html}

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#alert)

:::
