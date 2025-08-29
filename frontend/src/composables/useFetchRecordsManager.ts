import { ref, computed } from 'vue';
import type { Ref } from 'vue';
import FetchRecordsService from '@/services/fetchRecordsService';
import { StorageKey } from '@/utils/constants';

const storageType = window.sessionStorage;


interface BaseRecord {
  _id?: string;
  ticketNo?: string;
  eventid?: string;
  apipath?: string;
  payloadstr?: string;
  [key: string]: any;
}

type RecordType = 'reconciliation' | 'error' | 'ftp';

export function useFetchRecordsManager(type: RecordType) {
  const records = ref<BaseRecord[]>([]);
  const selectedRecord = ref<BaseRecord | null>(null);
  const apiError: Ref<string | null> = ref(null);
  const counts = ref<Record<string, number>>({});
  const service = FetchRecordsService;

  const fetchRecords = async (card: any) => {
    const cacheKey = `${StorageKey.EVENTS}_${type}_${card.type}`;
    const cached = storageType.getItem(cacheKey);

    if (cached) {
      try {
        records.value = JSON.parse(cached);
        selectedRecord.value = null;
        apiError.value = null;
        return;
      } catch (err) {
        console.warn('Failed to parse cached data:', err);
        storageType.removeItem(cacheKey);
      }
    }

    try {
      const response = await service.fetchRecords(type, card.type);
      const data = response.data || [];
      records.value = data;
      selectedRecord.value = null;
      apiError.value = null;
      storageType.setItem(cacheKey, JSON.stringify(data));
      await fetchRecordCount(card);
    } catch (err: any) {
      console.error('Fetch error:', err);
      apiError.value = `Error: ${err.response?.statusText || 'Unknown'}`;
    }
  };

  const fetchRecordCount = async (card: any): Promise<number> => {
    const countKey = `${StorageKey.EVENT_COUNT}_${type}_${card.type}`;
    const cachedCount = storageType.getItem(countKey);

    if (cachedCount !== null) {
      counts.value[card.type] = parseInt(cachedCount, 10);
      return counts.value[card.type];
    }

    try {
      const response = await service.fetchCount(type, card.type);
      const count = response.data.count ?? 0;
      counts.value[card.type] = count;
      storageType.setItem(countKey, count.toString());
      console.log(count);
      return count;
    } catch (err: any) {
      console.error('Count fetch error:', err);
      counts.value[card.type] = 0;
      return 0;
    }
  };

  const selectRecord = (record: BaseRecord) => {
    selectedRecord.value = record;
  };

  const refreshData = async (card: any) => {
    const eventKey = `${StorageKey.EVENTS}_${type}_${card.type}`;
    const countKey = `${StorageKey.EVENT_COUNT}_${type}_${card.type}`;
    storageType.removeItem(eventKey);
    storageType.removeItem(countKey);
    await fetchRecords(card);
  };

  const parsedPayload = computed(() => {
    if (type !== 'reconciliation') return null;
    if (!selectedRecord.value?.payloadstr) return '{}';

    try {
      let result = JSON.parse(selectedRecord.value.payloadstr);
      if (typeof result === 'string') result = JSON.parse(result);
      return JSON.stringify(result, null, 2);
    } catch (err) {
      console.error('Payload parse error:', err);
      return selectedRecord.value.payloadstr;
    }
  });

  return {
    records,
    selectedRecord,
    apiError,
    counts,
    fetchRecords,
    fetchRecordCount,
    selectRecord,
    refreshData,
    parsedPayload,
  };
}
