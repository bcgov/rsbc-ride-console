export function clearReconciliationCache() {
  Object.keys(sessionStorage).forEach((key) => {
    if (key.startsWith('RECON_EVENTS_')) {
      sessionStorage.removeItem(key);
    }
  });
}
