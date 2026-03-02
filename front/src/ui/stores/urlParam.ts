import { defineStore } from 'pinia'
import { computed, watch, reactive, type Ref } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useRoute } from 'vue-router'
import { useStorage } from '@vueuse/core'

type ParamValue = string | string[] | undefined
type Persistence = 'memory' | 'localStorage'
type Scope = 'global' | 'route'

const useParamCache = defineStore('ui-param-cache', () => {
    const memory = reactive(new Map<string, ParamValue>())
    const local = useStorage<Record<string, ParamValue>>('fw-url-param-cache', {})

    return {
        init: (config: { key: string, mode: Persistence }) => computed({
            get: () => config.mode === 'memory' ? memory.get(config.key) : local.value[config.key],
            set: (v: ParamValue) => {
                if (config.mode === 'memory') memory.set(config.key, v)
                else local.value[config.key] = v
            }
        }),

        // Observe these in the Vue Dev Tools:
        memory,
        local
    }
})

type NonnegativeInteger<T extends number> =
  `${T}` extends `-${any}` | `${any}.${any}` ? never : T

/**
 * Determine Ref type based on config object
 */
type InferDerivedType<C>
    = C extends { allowedValues: 'singleton' }
    ? string | undefined
    : C extends { allowedValues: 'array' }
    ? string[]
    : C extends { allowedValues: 'nonnegativeInteger' }
    ? NonnegativeInteger<number>
    : C extends { allowedValues: readonly (infer U)[] }
    ? U
    : ParamValue

/**
 * Persist an Url parameter across routes (and, optionally, reloads)
 *
 * @param name - Url parameter, e.g. `tags` in `?tags=a&tags=b`
 * @param config.persistence - Persist Url parameter in memory or local storage and eventually restore it when the user loads a page. Defaults to local storage.
 * @param config.scope - Limit the scope to the current route name or the whole app. Defaults to 'global'.
 * @param config.allowedValues - Whitelist a set of values. Force the parameter to have one of the allowed values at any time. Note that you cannot whitelist arrays so multiple values per parameter always default.
* - Choose `array` to interpret a single value `a` as `[a]`
* - Choose `singleton` to delete duplicate values
* - Choose `nonnegativeInteger` for values between 0 and infinity
 * @returns reactive, cached value, e.g. `['a', 'b']` in `?tags=a&tags=b`  - `''` and `null` are normalized to `undefined`
 * Its type implicitly depends on the type of `config.allowedValues`
 */
export function useUrlParamStore<
    const T extends string,
    const C extends {
        persistence?: Persistence
        scope?: Scope
        allowedValues?: readonly T[] | readonly [undefined, ...T[]] | 'array' | 'singleton' | 'nonnegativeInteger'
    }
>(
    name: string,
    config: C = {} as C
): Ref<InferDerivedType<C>> {
    const store = useParamCache()

    const transform = (v: ParamValue) =>
        config.allowedValues === 'singleton'
        ? Array.isArray(v) ? v[0] : v
        : config.allowedValues === 'array'
        ? (Array.isArray(v) ? v : v ? [v] : [])
        : config.allowedValues === 'nonnegativeInteger'
        ? Math.min(v && !Array.isArray(v) && parseInt(v) || 0, 0)
        : Array.isArray(config.allowedValues)
        ? config.allowedValues?.includes(v) ? v : config.allowedValues[0]
        : v

    const param = useRouteQuery(name, undefined, { transform })

    const route = useRoute()
    const cache = store.init({
        key: config.scope === 'route' && route.name
            ? `${String(route.name)}:${name}`
            : name,
        mode: config.persistence ?? 'memory'
    })

    if (!param.value && cache.value) {
        param.value = cache.value
    }

    watch(param, newValue => {
        if (newValue) cache.value = transform(newValue)
    }, { deep: true })

    return param as Ref<InferDerivedType<C>>
}
