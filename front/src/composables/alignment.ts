import type { Entries, Entry, KeysOfUnion } from 'type-fest'
import type { HTMLAttributes } from 'vue'

export type AlignmentProps = {
  alignText?: 'start' | 'center' | 'end' | 'stretch' | 'space-out',
  alignSelf?: 'start' | 'center' | 'end' | 'auto' | 'baseline' | 'stretch',
  alignItems?: 'start' | 'center' | 'end' | 'auto' | 'baseline' | 'stretch'
} & {
  [T in 'center' | 'stretch']?: true
}
export type Key = KeysOfUnion<AlignmentProps>

const styles = {
  center: 'place-content: center center; place-self: center center;',
  stretch: 'place-content: stretch stretch; place-self: stretch stretch;',
  alignText: (a:AlignmentProps['alignText']) => ({
    start: 'justify-content: flex-start;',
    center: 'place-content: center;',
    baseline: 'align-items: baseline;',
    end: 'justify-content: flex-end;',
    stretch: 'place-content: stretch;',
    'space-out': 'place-content: space-between;'
  }[a!]),
  alignSelf: (a:AlignmentProps['alignSelf']) => ({
    start: 'align-self: flex-start;',
    center: 'align-self: center;',
    end: 'align-self: flex-end;',
    auto: 'align-self: auto;',
    baseline: 'align-self: baseline;',
    stretch: 'align-self: stretch;'
  }[a!]),
  alignItems: (a:AlignmentProps['alignSelf']) => ({
    start: 'align-items: flex-start;',
    center: 'align-items: center;',
    end: 'align-items: flex-end;',
    auto: 'align-items: auto;',
    baseline: 'align-items: baseline;',
    stretch: 'align-items: stretch;'
  }[a!])
} as const

const getStyle = (props : Partial<AlignmentProps>) => ([key, value]: Entry<AlignmentProps>):string =>
  (
    typeof styles[key] === 'string'
      ? styles[key]
      // @ts-expect-error We know that props[key] is a value accepted by styles[key]. The ts compiler is not so smart.
      : (styles[key]((key in props && props[key]) ? props[((props[key]), (key))] : value))
  )

const merge = (rules: string[]) => (attributes: HTMLAttributes = {}) =>
  rules.length === 0
    ? attributes
    : ({
        ...attributes,
        style: rules.join(' ') + ('style' in attributes ? attributes.style + ' ' : '')
      })

// All keys are exclusive
const conflicts: Set<Key>[] = [
  new Set(['center', 'stretch']),
  new Set(['alignText']),
  new Set(['alignSelf'])
]

/**
 * Add alignment styles to your component.
 * Alignments are designed to work both in a grid and flex contexts but may fail in normal context.
 *
 * (1) Add `& AlignmentProps` to your `Props` type
 * (2) Call `v-bind="alignment(props)"` on your component template
 * (3) Now your component accepts width props such as `align-text="center"`.
 *
 * @param props Your component's props (or ...rest props if you have destructured them already)
 * @param defaults These props are applied immediately and can be overridden by the user
 * @param attributes Optional: To compose width, color, alignment, etc.
 * @returns the corresponding `{ style }` object
 */
export const align = <TProps extends Partial<AlignmentProps>>(
  props: TProps,
  defaults: Partial<AlignmentProps> = {}
) => merge(
    ((Object.entries(props) as Entries<TProps>).reduce(
      (acc, [key, value]) =>
        value && key in styles
          ? acc.filter(([accKey, _]) => !conflicts.find(set => set.has(accKey) && set.has(key)))
            .concat([[key, value]])
          : acc
      ,
    (Object.entries(defaults)) as Entries<Partial<AlignmentProps>>
    )).map(getStyle(props))
  )
