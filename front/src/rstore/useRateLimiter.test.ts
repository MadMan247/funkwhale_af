import { expect, test } from 'vitest'
import { useRateLimiter, type RateLimiterError, isRateLimiterError } from './useRateLimiter'

const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

const config = {
  cooldown: 10,
  supersedeWhen: (newTask: string, oldTask: string) => newTask.startsWith(oldTask),
  equalWhen: (newTask: string, oldTask: string) => newTask === oldTask
}

test('If not currently in cooldown, new task starts immediately', async () => {
  const { greenlight } = useRateLimiter<string>(config)
  let count = 0
  const operation = () => count = 1

  await greenlight('1')
  operation()

  expect(count).toBe(1)
})

test('If currently in cooldown, new, non-superseding task are deferred', async () => {
  const { greenlight } = useRateLimiter<string>(config);
  let count = 0;

  (async () => {
    await greenlight('A')
    count++
  })();

  (async () => {
    await greenlight('B')
    count++
  })()

  // Task A will not start synchronously
  expect(count).toBe(0)

  // It will finish asynchronously
  await wait(0)
  expect(count).toBe(1)

  // After the cooldown period, task B is expected to have finished
  await wait(config.cooldown)
  expect(count).toBe(2)
})

test('Superseded tasks are rejected', async () => {
  const { greenlight } = useRateLimiter<string>(config);
  const executedTasks: string[] = []

  // Tasks started outside of cooldown cannot be superseded
  const promiseA
    = greenlight('A').then(() => executedTasks.push('A'))

  // During cooldown, only the latest superseding task remains
  const promiseB_superseded
    = greenlight('B').then(() => executedTasks.push('B (should not run)'))

  const promiseB1_superseding
    = greenlight('B1').then(() => executedTasks.push('B1'))

  const promiseB11_superseding
    = greenlight('B11').then(() => executedTasks.push('B11'))

  // Non-superseding tasks are added to the end of the queue
  const promiseC
    = greenlight('C').then(() => executedTasks.push('C'))

  // Tasks can only supersede other tasks that were started during cooldown
  const promiseA1
    = greenlight('A1').then(() => executedTasks.push('A1'))

  const [resultA, resultB, resultB1, resultB11, resultC, resultA1] = await Promise.allSettled([
    promiseA,
    promiseB_superseded,
    promiseB1_superseding,
    promiseB11_superseding,
    promiseC,
    promiseA1
  ])

  expect(resultA.status).toBe('fulfilled')
  expect(resultB11.status).toBe('fulfilled')
  expect(resultC.status).toBe('fulfilled')
  expect(resultA1.status).toBe('fulfilled')

  expect(resultB.status).toBe('rejected')
  expect(((resultB as PromiseRejectedResult).reason as RateLimiterError).name).toBe('RateLimitedTaskSuperseded')
  expect(isRateLimiterError((resultB as PromiseRejectedResult).reason)).toBe(true)

  expect(resultB1.status).toBe('rejected')
  expect(((resultB1 as PromiseRejectedResult).reason as RateLimiterError).name).toBe('RateLimitedTaskSuperseded')
  expect(isRateLimiterError((resultB1 as PromiseRejectedResult).reason)).toBe(true)

  expect(executedTasks).toEqual(['A', 'B11', 'C', 'A1'])
})
