export const preventNonNumeric = (e: KeyboardEvent) => {
  if (!e.key.match(/![0-9]$/)) {
    e.preventDefault()
  }
}
