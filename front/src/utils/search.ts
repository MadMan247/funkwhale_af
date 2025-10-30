export interface Token {
  field: string | null
  value: string
}

/**
 * Normalizes a query string by splitting it into tokens while respecting quoted phrases.
 *
 * @param query - The input query string to normalize
 * @returns Array of normalized tokens with quoted phrases preserved as single tokens
 *
 * @example
 * ```
 * normalizeQuery('this is "my query" go')
 * // Returns: ['this', 'is', 'my query', 'go']
 * ```
 */
export function normalizeQuery (query: string): string[] {
  if (!query) return []

  const match = query.match(/\\?.|^$/g)
  if (!match) return []

  const { tokens } = match.reduce((state, c) => {
    if (c === '"') {
      state.quote ^= 1
    } else if (!state.quote && c === ' ') {
      state.tokens.push('')
    } else {
      state.tokens[state.tokens.length - 1] += c.replace(/\\(.)/, '$1')
    }

    return state
  }, { tokens: [''], quote: 0 })

  return tokens
}

const unquote = (str: string) => {
  if (str[0] === '"') str = str.slice(1)
  if (str[str.length - 1] === '"') str = str.slice(0, -1)
  return str
}

const quoteIfNecessary = (str: string) =>
  str.includes(' ')
      ? `"${str}"`
      :  str

/**
 * Parses an array of normalized query tokens into structured Token objects.
 *
 * @param normalizedQuery - Array of tokens as returned by normalizeQuery
 * @returns Array of Token objects with field and value properties
 *
 * @example
 * ```
 * parseTokens(['status:pending', 'hello'])
 * // Returns:
 * // [
 * //   { field: 'status', value: 'pending' },
 * //   { field: null, value: 'hello' }
 * // ]
 * ```
 */
export const parseTokens = (normalizedQuery: string[]): Token[] =>
  normalizedQuery.map(t => {
    // Split the token on ":" to separate field from value
    const parts = t.split(/:(.+)/)
    return parts.length === 1
      ? { field: null, value: t }  // No field specified
      : { field: parts[0]!, value: unquote(parts[1]!) }  // Field:value format, remove quotes
  })

/**
 * Compiles an array of Token objects back into a query string.
 *
 * @param tokens - Array of Token objects as returned by parseTokens
 * @returns A formatted query string
 */
export const compileTokens = (tokens: Token[]) =>
  tokens.map(({field, value}) => field
    ? `${field}:${quoteIfNecessary(value)}`
    : quoteIfNecessary(value)
  )
  .join(' ')
