# Contributing

[[toc]]

## Setting up your IDE

If you are using vscode, [enable `Vue` code hints in the `.md`
docs](https://vitepress.dev/guide/using-vue#vs-code-intellisense-support):

```json
// .vscode/settings.json
"vue.server.includeLanguages": ["vue", "markdown"]
```

## Adding new UI components

::: tip Prerequisites

✔ I am using the same pattern in many different places in the app

✔ The pattern is not coupled with any funkwhale types

✔ It's a conventional UI pattern

:::

1. Create a file `Xyz.vue` at `src/components/ui` and code the component
2. Add a file `xyz.md` at `ui-docs/components` with exhaustive examples
3. In `ui-docs/.vitepress/config.ts`, add the component to the sidebar links

Make sure to follow the [anatomy of a Component](./using-components#anatomy-of-a-component-file)!
