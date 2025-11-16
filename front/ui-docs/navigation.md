---
layout: page
---

<script setup lang="ts">
// TODO: flesh out
</script>

<div id="is-overview-page" />

# Navigation and _Changes of Context_

::: info What is a change of context?

> **changes of context**: major changes that, if made without user awareness, can disorient users who are not able to view the entire page simultaneously

> **Example**<br /> Opening a new window, moving focus to a different component, going to a new page (including anything that would look to a user as if they had moved to a new page) or significantly re-arranging the content of a page are examples of changes of context.

Source: [https://www.w3.org/WAI/WCAG22/Understanding/change-on-request.html#dfn-changes-of-context](https://www.w3.org/WAI/WCAG22/Understanding/change-on-request.html#dfn-changes-of-context)

:::

**Components that may change the context:**

- [Link](components/ui/link)
- [Pagination](components/ui/pagination)
- [Table of Contents](components/ui/toc)
- [Tabs (deprecated in favor of Nav)](components/ui/tabs)
- [Nav](components/ui/nav)
- [Modal](components/ui/modal)

::: tip Designing user flows

## Accessible Navigation

1. Understand where in your UX the context changes. If only a small part of the page changes, it's not a context change, and you should not tap into the browser's navigation history.
2. Make context changes predictable and operable

- Ideally, <mark>let users initiate the context change</mark> by clicking a well-labeled link
- If the context changes as a result of an action triggered by a button, make sure to inform the user beforehand about the potential context change.
- Allow users to 'go back' by leveraging the navigation history or by providing obvious controls (Escape key, Close button, Cancel button)

3. Test your page with a screen reader and make sure the announcements make sense. Use [the Alert component](components/ui/alert) with an appropriate `role` prop, or add the `role` attribute to any element that announces the change. Cover all possible user flows.
4. Make user flows explicit and declarative so that future contributors and developers have an easy time iterating on the page.
