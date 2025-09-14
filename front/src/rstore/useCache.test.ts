import { expect, test } from 'vitest'
import { useCache } from './useCache'

const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
const retention = 10

test('Cache sets value synchronously', () => {
  const cache = useCache({ retention })

  cache('K').value = ('V')
  expect(cache('K').value).toBe('V')
})

test('Cache forgets value after a set time', async () => {
  const cache = useCache({ retention })

  cache('K').value = ('V')
  await wait(retention);
  expect(cache('K').value).toBe(undefined)
})
