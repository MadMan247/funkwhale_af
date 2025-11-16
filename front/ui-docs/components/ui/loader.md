---
layout: page
---

<script setup lang="ts">
import Loader from '@ui/Loader.vue'

import LoaderA11y from '@/examples/Loader.a11y.vue'
</script>

<style>
.docs-loader-container div[style^=width] {
  border: 1px solid #666;
  height: 2em;
}
</style>

```ts
import Loader from "@ui/Loader.vue"
```

# Loader

Loaders visually indicate when an operation is loading. This makes it visually clear that the user can't interact with the element until the loading process is complete.

## Maintaining component accessibility

To ensure the loader component remains accessible:

1. Verify the loader has an appropriate ARIA live region to announce its state
2. Test that the loading state is properly announced by screen readers
3. Ensure the loader has sufficient color contrast against its background
4. Verify the loader animation stops after 4.9s to avoid excessive motion
5. Confirm that any interactive elements are properly disabled during loading

## For Authors and Designers

### A11y Checklist

- [ ] Add descriptive text that explains what is loading (e.g., "Loading profile data...")
- [ ] Ensure proper ARIA attributes are used (`aria-busy="true"` on loading content)
- [ ] Consider providing an estimated time or progress indicator for long operations
- [ ] Maintain WCAG 2.2 minimum contrast ratio (4.5:1) between loader and background
- [ ] Test with reduced motion preferences enabled

| Prop        | Data type | Required? | Description                                  |
| ----------- | --------- | --------- | -------------------------------------------- |
| `container` | Boolean   | No        | Whether to create a container for the loader |

> [!NOTE]
> To avoid extended periods of distraction, the spinner animation stops after 4.9s.
>
> [Continuous movement is distracting for some users](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) and not necessary to convey the ongoing loading state. A load time beyond 5s is very unlinkely and would usually indicate lost connection or an unhandled error. In either case, the user cannot expect to see results eventually, so the animated spinner would give a false impression.

## Normal loader

```vue-html
<div style="width: 50%">
  <Loader />
</div>
```

<div class="docs-loader-container">
  <div style="width: 50%">
    <Loader />
  </div>
</div>

## No container

By default the `<fw-loader />` component creates a container that takes up 100% of its parent's height. You can disable this by passing a `:container="false"` property. The loader renders centered in the middle of the first parent that has `position: relative` set.

```vue-html
<div style="position: relative">
  <div style="width: 50%">
    <Loader :container="false" />
  </div>
</div>
```

<div class="docs-loader-container">
  <div style="position: relative">
    <div style="width: 50%">
      <Loader :container="false" />
    </div>
  </div>
</div>

::: tip Using this component

## A11y Checklist

- [ ] The loader has sufficient contrast (3:1) against its background for the animation to be visible. Use appropriate color props on the background. [1.4.11](https://accessibility.education.gov.uk/guidelines/wcag/explorer#1-4-11)
- [ ] For loading times over 10 seconds, provide either time estimates or progress indicators. [2.2.1](https://accessibility.education.gov.uk/guidelines/wcag/explorer#2-2-1)
- [ ] For critical loading states that block user interaction:
  - [ ] Add descriptive text that explains what is loading (e.g., "Loading your profile..."). [3.3.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#3-3-2)
  - [ ] Consider using `role="status"` with `aria-busy="true"` on the container of the loading content. [4.1.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#4-1-2)
  - [ ] Ensure any blocked interactive elements are properly disabled. [4.1.2](https://accessibility.education.gov.uk/guidelines/wcag/explorer#4.1.2)
- [ ] For decorative loaders (e.g., indicating background content fetch):
  - [ ] Add `aria-hidden="true"` to prevent unnecessary announcements
  - [ ] Ensure the loading state is conveyed through other means (e.g., "Refreshing..." button text)

## Accessible loader

<LoaderA11y class="default"/>

[Test this component in isolation against WCAG2 criteria](/maintaining-accessibility#loader)

:::
