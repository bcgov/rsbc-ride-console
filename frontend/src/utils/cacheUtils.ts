export function clearCache() {
  Object.keys(sessionStorage).forEach((key) => {
    if (key.startsWith('EVENT')) {
      sessionStorage.removeItem(key);
    }
  });
}
