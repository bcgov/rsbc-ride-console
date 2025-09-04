// composables/useErrorUpdater.ts

import ErrorUpdateService from '@/services/errorUpdateService';
import FetchRecordsService from '@/services/fetchRecordsService';
import { StorageKey } from '@/utils/constants';

const storageType = window.sessionStorage;

function getCacheKeys(type: string) {
  return {
    dataKey: `${StorageKey.EVENTS}_error_${type}`,
    countKey: `${StorageKey.EVENT_COUNT}_error_${type}`,
  };
} 

async function invalidateAndRefresh(type: string) {
  const { dataKey, countKey } = getCacheKeys(type);

  storageType.removeItem(dataKey);
  storageType.removeItem(countKey);

  const response = await FetchRecordsService.fetchRecords('error', type);
  const countRes = await FetchRecordsService.fetchCount('error', type);

  storageType.setItem(dataKey, JSON.stringify(response.data || []));
  storageType.setItem(countKey, String(countRes.data.count ?? 0));
}

export function useErrorUpdater() {
  const setFixedById = async (type: string, objectId: string) => {
    await ErrorUpdateService.setFixedById(objectId);
    await invalidateAndRefresh(type);
  };

  const setUnderAnalysisById = async (type: string, objectId: string) => {
    await ErrorUpdateService.setUnderAnalysisById(objectId);
    await invalidateAndRefresh(type);
  };

  const setAllFixed = async (type: string) => {
    await ErrorUpdateService.setAllFixed();
    await invalidateAndRefresh(type);
  };

  const setAllUnderAnalysis = async (type: string) => {
    await ErrorUpdateService.setAllUnderAnalysis();
    await invalidateAndRefresh(type);
  };

  return {
    setFixedById,
    setUnderAnalysisById,
    setAllFixed,
    setAllUnderAnalysis,
  };
}
