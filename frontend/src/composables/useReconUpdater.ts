import ReconUpdateService from '@/services/reconUpdateService';
import FetchRecordsService from '@/services/fetchRecordsService';
import { StorageKey } from '@/utils/constants';

const storageType = window.sessionStorage;

function getCacheKeys(type: string) {
  return {
    dataKey: `${StorageKey.EVENTS}_reconciliation_${type}`,
    countKey: `${StorageKey.EVENT_COUNT}_reconciliation_${type}`,
  };
}

async function invalidateAndRefresh(type: string) {
  const { dataKey, countKey } = getCacheKeys(type);

  // Clear cache
  storageType.removeItem(dataKey);
  storageType.removeItem(countKey);

  // Refresh data
  const response = await FetchRecordsService.fetchRecords('reconciliation', type);
  const countRes = await FetchRecordsService.fetchCount('reconciliation', type);

  storageType.setItem(dataKey, JSON.stringify(response.data || []));
  storageType.setItem(countKey, String(countRes.data.count ?? 0));
}

export function useReconUpdater() {
  // Unified reset for all items of a given type
  const resetAllByType = async (type: string) => {
    await ReconUpdateService.resetAllByType(type);
    await invalidateAndRefresh(type);
  };

  // Unified reset for a single item of a given type
  const resetById = async (type: string, objectId: string) => {
    await ReconUpdateService.resetById(type, objectId);
    await invalidateAndRefresh(type);
  };

  // DELETE
  const deleteEventById = async (type: string, objectId: string) => {
    await ReconUpdateService.deleteEventById(type, objectId);
    await invalidateAndRefresh(type);
  };

  const deleteAllEvents = async (type: string) => {
    await ReconUpdateService.deleteAllEvents(type);
    await invalidateAndRefresh(type);
  };

  return {
    resetAllByType,
    resetById,
    deleteEventById,
    deleteAllEvents,
  };
}
