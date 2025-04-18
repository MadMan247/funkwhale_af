# Using Components

We distinguish between components that are coupled with funkwhale-specific datatypes and "pure" user interface components:

- Funkwhale-specific components such as `Activity` or `AlbumCard` import from `types.ts`.
- Pure UI components (found in `src/components/ui`) are independent from Funkwhale. Think of `Button`, `Tabs` or `Layout`

---

[[toc]]

## Anatomy of a component file

### Imports

First, import vue features and external libraries. Add the sub-components you want to use last. Order each block of imports by alphabet to prevent commit diff noise.

### Script

Add a blank line between Imports and script. Use modern typescript-friendly features such as `defineModel` and `defineProps` [as documented in the Vue Docs](https://vuejs.org/api/sfc-script-setup.html#definemodel) instead of Macros.

### Template

If you are new to Vue, read the docs, especially [the chapter about Single-File Components](https://vuejs.org/guide/scaling-up/sfc), to get familiar.

### Style

Don't pollute the global namespace. Funkwhale compiles a single stylesheet (used in the app, the blog and the website). If you need specific styles in your component, use vue's [SFC features](https://vuejs.org/api/sfc-css-features.html#sfc-css-features) such as `module`. Vue will give you a `$style` object containing all locally defined classes.

```vue
<script setup>
import { ref } from "vue";
const theme = ref({
  color: "red"
});
</script>

<style module>
.content {
  color: v-bind("theme.color");
}
</style>

<template>
  <div :class="$style.content"></div>
</template>
```

::: details Tip: Debugging styles

We have enabled [the vite feature `css.devSourcemap: true`](https://v2.vitejs.dev/config/#css-devsourcemap) so that in your browser devtools, you can trace the code responsible for module styles:

<img alt="For each class, the browser devTools will link the corresponding `<style module>` code" width="420" src="data:image/png;base64,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" />

:::

::: info What about the global style?

As of now, class and variable names from the global styles are not available as typescript objects. We should definitely add this feature at some point.

:::

## Using UI components in your views

```vue
<script setup>
import Alert from "~/components/ui/Alert.vue";
import Button from "~/components/ui/Button.vue";
</script>

<style module></style>

<template>
  <Alert yellow />
  <Button />
</template>
```

## Limitations of component props

While Vue can infer props based on a type, it will fail with mysterious errors if the type is an exclusive union or has union types as keys.

I hope this will be resolved soon so we can use this more elegant way of injecting non-trivial props with full autocomplete, 21st century style:

```vue
<script setup>
type A = 'either' | 'or'
type B = 'definitely'
type Props = { [k in `${A}-${B}`]?: true }
</script>

<template>
  <Component either-definitely />
  <Component or-definitely />
  <Component />
  {{ Error: <Component either /> }} {{ Error: <Component definitely /> }}
</template>
```

::: details Example

````ts
// Color from props

type SingleOrNoProp<T extends string> = RequireOneOrNone<Record<T, true>, T>;
type SingleProp<T extends string> = RequireExactlyOne<Record<T, true>, T>;

export type Props = Simplify<
  SingleProp<Color | Default | Pastel> &
    SingleOrNoProp<Variant> &
    SingleOrNoProp<"interactive"> &
    SingleOrNoProp<"raised">
>;

// Limit the choices:

export type ColorProps = Simplify<
  SingleProp<Color> & SingleOrNoProp<Variant> & SingleOrNoProp<"raised">
>;

export type PastelProps = Simplify<
  SingleProp<Pastel> & SingleOrNoProp<"raised">
>;

// Note that as of now, Vue does not support unions of props.
// So instead, we give it a single string:

export type ColorProp = Simplify<`${Color}${
  | ""
  | `-${Variant}${"" | "-raised"}`}`>;
export type PastelProp = Simplify<`${Pastel}${"" | "-raised"}`>;

// Using like this:
//   type Props = {...} & { [k in ColorProp]? : true }
// This will also lead to runtime errors. Why?

export const isColorProp = (k: string) =>
  !![...colors, ...defaults, ...pastels].find(k.startsWith);

console.log(true, isColorProp("primary"));
console.log(true, isColorProp("secondary"));
console.log(true, isColorProp("red"));
console.log(false, isColorProp("Jes"));
console.log(false, isColorProp("raised"));

/**
 * Convenience function in case you want to hand over the props in the form
 * ```
 * <Component primary solid interactive raised >...</Component>
 * ```
 *
 * @param props Any superset of type `Props`
 * @returns the corresponding `class` object
 *
 * Note: Make sure to implement the necessary classes in `colors.scss`!
 */
export const colorFromProps = (props: Record<string, unknown>) =>
  color(
    Object.keys(props)
      .filter(isColorProp)
      .join(" ")
      .replace("-", " ") as ColorSelector
  );
````

:::
