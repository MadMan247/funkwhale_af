# Contributing

[[toc]]

## Setting up your IDE

If you are using _vscode_, [enable `Vue` code hints in the `.md`
docs](https://vitepress.dev/guide/using-vue#vs-code-intellisense-support):

```json
// .vscode/settings.json
"vue.server.includeLanguages": ["vue", "markdown"]
```

I (flupsi) recommend [the quick, free editor _zed_](https://zed.dev) with the default `Vue` extension.

## Setting up a reproducible environment

To set up a reproducible environment independent from your system's installed software packages, use `docker` or `mise`.

Read the [funkwhale docs about docker here](https://docs.funkwhale.audio/developer/setup/docker.html).

To quickly run tests, linters, etc. locally, you don't need to install `node` or `yarn` globally.

1. [Install mise](https://mise.jdx.dev/)
2. Run `mise use yarn@1` to enable the `yarn` command in your current shell
3. Now you can run all commands such as `yarn dev:docs` or `yarn lint` without installing funkwhale-specific tools on your system globally.

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
