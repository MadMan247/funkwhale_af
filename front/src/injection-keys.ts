import { type InjectionKey, type Ref } from 'vue'
import { type RouterLinkProps } from 'vue-router'

export type TabProps = {
  title: string,
  to?: RouterLinkProps['to']
  icon?: string
}

export const TABS_INJECTION_KEY = Symbol('tabs') as InjectionKey<{
  tabs: TabProps[]
  currentTitle: Ref<TabProps['title']>
}>

export interface PopoverContext {
  items: Ref<number>
  hoveredItem: Ref<number>
}

export const POPOVER_INJECTION_KEY = Symbol('popover') as InjectionKey<Ref<boolean>[]>
export const POPOVER_CONTEXT_INJECTION_KEY = Symbol('popover context') as InjectionKey<PopoverContext>
