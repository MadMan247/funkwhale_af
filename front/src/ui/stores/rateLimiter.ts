import hash from 'stable-hash'

import { defineStore } from 'pinia'
import { ref } from 'vue'

export type RateLimiterError = {
  name: 'RateLimitedTaskSuperseded'
  message: string
}

export const isRateLimiterError = (e: Error) => e.name === 'RateLimitedTaskSuperseded'

/**
 * Queued-up tasks start immediately if cooldown period is over. Else, they are postponed to keep the minimum waiting time
 * between consecutive tasks.
 * An older planned task is replaced (superseded) by a newer one if they match via `supersedeWhen`.
 * This way, you can prevent excessively long trails, for example when an input triggers tasks on each keystroke.
 *
 * @param cooldown: Minimum waiting time between two consecutive tasks. Good values might be around 50-500ms.
 * Default: 50ms (20x per second)
 * Tasks coming in at a slower rate are executed immediately.
 */
export const useRateLimiterStore = defineStore('rateLimiter', () => {
  const config = ref<{
    cooldown: number
    isDisabled: boolean
  }>({
    cooldown: 50,
    isDisabled: false
  })

  type Key = unknown
  type Id = number
  const queue = ref<[Key, Id][]>([])
  let counter:Id = 0

  const cooldown = () => new Promise((resolve) => setTimeout(resolve, config.value.cooldown))

  /**
   * Delays or cancels a task to keep the rate of costly operations below 1x per `cooldown`
   *
   * @param key: Use a single key per widget to prevent unnecessary fetches.
   * * New tasks will supersede the older ones already in the queue with the same key.
   * * When the user triggers multiple fetches with the same key in quick succession, only the latest one will be executed.
   * * You can use objects as keys. They are compared via their stable hash.
   * @param taskConfig.priority: (optional) `true` inserts the new task next in the queue.
   * No value (default) adds it to the end of the queue.
   * @returns a promise that resolves when the task can be executed, or throws if it has been superseded by a task greenlit later.
   */
  const greenlight = async <T extends Key>(
    key: T,
    {  priority }: {
        priority?: true
    } = {}
) => {
    if (config.value.isDisabled) return

    // Current time serves as identity for self
    const id = counter++

    // 1. Add self to queue
    if (queue.value.length === 0) {
      queue.value = [[key, id]]
    } else {
      queue.value = queue.value.filter(([k, _]) => k !== key)
      queue.value = priority ? [[key, id], ...queue.value] : [...queue.value, [key, id]]
    }

    // 2. Wait for other, higher-priority tasks if necessary
    while (queue.value.at(0)?.[1] !== id) {
      if (!queue.value.find(([k, _]) => hash(k) === hash(key))) throw {
        name: 'RateLimitedTaskSuperseded',
        message: `Task ${key} has been superseded by a newer task. Queue is now: ${queue.value  }`
      } satisfies RateLimiterError
      await cooldown()
    }

    // 3. Remove self from queue after cooldown
    (async () => {
      await cooldown()
      queue.value = queue.value.filter(([_, id_]) => id_ !== id)
    })()
  }

  return { config, queue, greenlight }
})
