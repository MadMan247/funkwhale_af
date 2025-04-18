import type { Entries, KeysOfUnion } from 'type-fest'
import type { HTMLAttributes } from 'vue'

export type WidthProps =
  | { minContent?: true }
  | { iconWidth?: true }
  | { tiny?: true }
  | { buttonWidth?: true }
  | { small?: true }
  | { medium?: true }
  | { auto?: true }
  | { full?: true }
  | { grow?: true }
  | { width?: string }
  | { square?: true }
  | { squareSmall?: true }
  | { lowHeight?: true }
  | { normalHeight?: true }
export type Key = KeysOfUnion<WidthProps>

const widths = {
  minContent: 'width: min-content; flex-grow: 0;',
  iconWidth: 'width: 40px;',
  tiny: 'width: 124px; --grid-column: span 2;',
  buttonWidth: 'width: 136px; --grid-column: span 2; flex-grow: 0; min-width: min-content;',
  small: 'width: 202px; --grid-column: span 3;',
  medium: 'width: 280px; --grid-column: span 4;',
  auto: 'width: auto;',
  full: 'width: auto; --grid-column: 1 / -1; place-self: stretch;',
  grow: 'flex-grow: 1;',
  width: (w: string) => `width: ${w}; flex-grow:0;`
} as const

const sizes = {
  squareSmall: 'height: 40px; width: 40px; padding: 4px; justify-content: center;',
  square: 'height: 48px; width: 48px; justify-content: center;',
  lowHeight: 'height: 40px;',
  normalHeight: 'height: 48px;'
} as const

const styles = {
  ...widths, ...sizes
} as const satisfies Record<Key, string | ((w: string) => string)>

// The `lint:tsc` script more errors here than the language server is happy.
// TODO: Fix this Issue: https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/2437
const getStyle = (props: Partial<WidthProps>) => (key: Key):string =>
  key in props
    ? typeof styles[key] === 'function'
      // @ts-expect-error Typescript is hard. Make the typescript compiler understand `key in props`
      ? styles[key](props[key])
      : styles[key] as string
    : ''

// All keys are exclusive
const conflicts: Set<Key>[] = [
  new Set(Object.keys(widths) as Key[]),
  new Set(Object.keys(sizes) as Key[])
]

const merge = (rules: string[]) => (attributes: HTMLAttributes = {}) =>
  rules.length === 0
    ? attributes
    : ({
        ...attributes,
        style: rules.join(' ') + ('style' in attributes ? ' ' + attributes.style : '')
      })

/**
 * Add a width style to your component.
 * Widths are designed to work both in a page-grid context and in a flex or normal context.
 *
 * (1) Add `& WidthProps` to your `Props` type
 * (2) Call `v-bind="width(props)"` on your component template
 * (3) Now your component accepts width props such as `small`, `medium`, `stretch`.
 *
 * @param props Your component's props (or ...rest props if you have destructured them already)
 * @param defaults These props are applied immediately and can be overridden by the user
 * @param attributes Optional: To compose width, color, alignment, etc.
 * @returns the corresponding `{ style }` object
 */
export const width = <TProps extends Partial<WidthProps>>(
  props: TProps,
  defaults: Key[] = []
) => merge(
    (Object.entries(props) as Entries<TProps>).reduce(
      (acc, [key, value]) =>
        value && key in styles
          ? acc.filter(accKey => !conflicts.find(set => set.has(accKey) && set.has(key)))
            .concat([key])
          : acc
      ,
      defaults
    ).map(getStyle(props))
  )
