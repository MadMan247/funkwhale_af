---
layout: page
---

<div id="is-overview-page" />

# Contributing

**Jump to chapter:**

[[toc]]

## Setting up your development environment

If you are using _vscode_, [enable `Vue` code hints in the `.md`
docs](https://vitepress.dev/guide/using-vue#vs-code-intellisense-support):

```json
// .vscode/settings.json
"vue.server.includeLanguages": ["vue", "markdown"]
```

I (flupsi) recommend [the quick, free editor _zed_](https://zed.dev) with the default `Vue` extension.

### DX and reproducibility

To set up a reproducible environment independent from your system's installed software packages, use `docker` or `mise`.

Read the [funkwhale docs about docker here](https://docs.funkwhale.audio/developer/setup/docker.html).

To quickly run tests, linters, etc. locally, you don't need to install `node` or `yarn` globally.

1. [Install mise](https://mise.jdx.dev/)
2. Run `mise use yarn` to enable the `yarn` command in your current shell
3. Now you can run all commands documented in `package.json` without installing any funkwhale-specific tools or starting containers on your system globally.

### Feedback loop

Make sure to run `yarn dev:docs` while editing your components to see changes on-the-fly. Run `yarn lint` periodically or set up your editor to get `eslint` annotations while editing your code.

## Discussing and proposing changes

[Getting started [Funkwhale Docs]](https://docs.funkwhale.audio/develop/developer/index.html)

[How to edit the UI strings [Funkwhale Docs]](https://docs.funkwhale.audio/develop/developer/contribute/copy.html) - [How to add translations [Funkwhale Docs]](https://docs.funkwhale.audio/develop/contributor/translation.html)

## Adding new UI components

::: info Prerequisites

✔ I am using the same pattern in many different places in the app

✔ The pattern is not coupled with any funkwhale types

✔ It's a conventional UI pattern

:::

::: tip Step by step

- [ ] (1) Create a file `Xyz.vue` at `src/components/ui` and code the component
- [ ] (2) Add a file `xyz.md` at `ui-docs/components` with exhaustive examples (You can place example files into the `ui-docs/examples` directory)
- [ ] (3) In `ui-docs/.vitepress/config.ts`, add the component to the sidebar links
- [ ] (4) Create an accessible example `ui-docs/examples/Xyz.a11y.vue` and describe how page authors can use the new component in an accessible way
- [ ] (5) Add the accessible example to [the Accessibility overview](/maintaining-accessibility) and document the necessary tests to verify its functioning and prevent regressions.

Make sure to follow the [anatomy of a Component](/using-components#anatomy-of-a-component-file), [avoid unnecessary barriers to funkwhale users [MDN]](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides) and [keep them accessible](/maintaining-accessibility).

:::
