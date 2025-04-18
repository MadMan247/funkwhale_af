import type { KeysOfUnion } from 'type-fest'
import type { HTMLAttributes } from 'vue'

export type DefaultProps =
  | { default?: true }
export type Default = KeysOfUnion<DefaultProps>

export type ColorProps =
  | { primary?: true }
  | { secondary?: true }
  | { destructive?: true }
export type Color = KeysOfUnion<ColorProps>

export type PastelProps =
  | { red?: true }
  | { blue?: true }
  | { purple?: true }
  | { green?: true }
  | { yellow?: true }
export type Pastel = KeysOfUnion<PastelProps>

export type VariantProps =
  | { solid?: true }
  | { outline?: true }
  | { ghost?: true }
export type Variant = KeysOfUnion<VariantProps>

export type InteractiveProps =
  | { interactive?: true }
export type Interactive = KeysOfUnion<DefaultProps>

export type RaisedProps =
  | { raised?: true }
export type Raised = KeysOfUnion<RaisedProps>

/* Props to Classes */

export type Props =
  (DefaultProps | ColorProps | PastelProps) & VariantProps & InteractiveProps & RaisedProps

export type Key =
  KeysOfUnion<Props>

// You can only have one color
const conflicts: Set<Key>[] = [
  new Set(['default', 'primary', 'secondary', 'destructive', 'red', 'blue', 'purple', 'green', 'yellow']),
  new Set(['solid', 'outline', 'ghost'])
]

const classes = {
  default: 'default',
  primary: 'primary',
  secondary: 'secondary',
  destructive: 'destructive',
  red: 'red',
  blue: 'blue',
  purple: 'purple',
  green: 'green',
  yellow: 'yellow',
  outline: 'outline',
  ghost: 'ghost',
  solid: 'solid',
  raised: 'raised',
  interactive: 'interactive'
} satisfies Record<Key, string>

const getPrecedence = (searchKey:Key | string) =>
  Object.entries(classes).findIndex(([key, _]) => key === searchKey)

/**
 * @param props A superset of `{ Key? : true }`
 * @returns the number of actually applied classes (if there are no defaults)
 */
export const isNoColors = (props: Partial<Props>) =>
  !color(props)().class

const merge = (classes: string[]) => (attributes: HTMLAttributes = {}) =>
  classes.length === 0
    ? attributes
    : ({
        ...attributes,
        class: classes.join(' ') + ('class' in attributes ? attributes.class + ' ' : '')
      })

/**
 * Add color classes to your component.
 * Color classes are defined in `colors.scss`. Make sure to implement the correct style there!
 *
 * (1) Add a subset of `& (DefaultProps | ColorProps | PastelProps) & VariantProps & InteractiveProps & RaisedProps` to your `Props` type
 * (2) Call `v-bind="color(props)"` on your component template
 * (3) Now your component accepts color props such as `secondary outline raised`.
 *
 * Composable with `width`, `color`, `alignment`, etc.
 *
 * @param props Your component's props (or ...rest props if you have destructured them already)
 * @param defaults These props are applied immediately and can be overridden by the user
 * @returns a function from the resulting attributes the corresponding `class` object
 */
export const color = (props: Partial<Props>, defaults?: Key[]) =>
  merge(
    Object.entries(props)
      .sort(([a, _], [b, __]) => getPrecedence(a) - getPrecedence(b))
      .reduce(
        (acc, [key, value]) =>
          value && key in classes
            ? acc.filter(accKey => !conflicts.find(set => set.has(accKey) && set.has(key as Key)))
              .concat([key as Key])
            : acc
        ,
        defaults || []
      )
  )

type ColorSelector =
  `${Color | Pastel | Default}${'' | ` ${Variant}${'' | ' interactive'}${'' | ' raised'}`}`

// Convenience function for applying default colors. Prefer using `color`
export const setColors = (color: ColorSelector) =>
  ({ class: color })
