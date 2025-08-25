export type RateLimiterError = {
  name: 'RateLimitedTaskSuperseded';
  message: string;
}

export const isRateLimiterError = (e: Error) =>
  e.name === 'RateLimitedTaskSuperseded'

/**
 * Queued-up tasks start immediately if cooldown period is over. Else, they are postponed to keep the minimum waiting time
 * between consecutive tasks.
 * An older planned task is replaced (superseded) by a newer one if they match via `supersedeWhen`.
 * This way, you can prevent excessively long trails, for example when an input triggers tasks on each keystroke.
 *
 * @param cooldown: Minimum waiting time between two consecutive tasks. Good values might be around 100-500ms.
 * Tasks coming in at a slower rate are executed immediately.
 * @param supersedeWhen: A task planned earlier will be replaced by the new task if this predicate holds true. Note that only future tasks can be replaced.
 * @param equalWhen: Used to check if task is still in the queue.
 */
export const useRateLimiter = <T>({ cooldown, supersedeWhen, equalWhen }: {
  cooldown: number,
  supersedeWhen: (newTask: T, oldTask: T) => boolean,
  equalWhen: (newTask: T, oldTask: T) => boolean
}) => {

  // The queue contains all tasks planned for the next tick
  let queue: T[] = [];

  const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  /**
   * Delays or cancels a task to keep the rate of costly operations below 1x per `cooldown`
   *
   * @param task: A unique(!), comparable label to identify the costly operation. Use JSON.stringify or an 'id' or 'key' field.
   * @param priority: (optional) `true` inserts the new task next in the queue. `replaceAll` additionally removes other tasks. No value (default) adds it to the end op the queue.
   * @returns a promise that resolves when the task can be executed, or throws if it has been superseded by a task greenlit later.
   */
  const greenlight = async (task: T, priority?: true | 'replaceAll') => {

    if (queue.length === 0 || priority === 'replaceAll') {

      // Initialize a new queue
      queue = [task]

    } else {

      // Remove any superseded older tasks
      queue = queue.filter(t =>
        !supersedeWhen(task, t)
      )

      // Insert new task into queue
      queue = priority
        ? [task, ...queue]
        : [...queue, task]

    }

    // Wait until the task is next. If the task has been superseded, throw a rejection message
    while (queue.at(0) !== task) {
      if (!queue.find(t => equalWhen(task, t))) throw ({
        name: 'RateLimitedTaskSuperseded',
        message: `Task ${task} has been superseded by a newer task`
      } satisfies RateLimiterError)
      await wait(cooldown);
    }

    // In the background, schedule the progression of the queue
    (async () => {
      await wait(cooldown);

      queue = queue.filter(t => t !== task)
    })();

    // Return immediately, resolving the promise for the caller.
    return;
  }

  return { greenlight }
}
