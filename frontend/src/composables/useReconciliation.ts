import { ref, computed, onMounted } from 'vue';
import type { Ref } from 'vue'; 
import ReconService from '@/services/reconService';
import { StorageKey } from '@/utils/constants';

const storageType = window.sessionStorage;

interface ReconciliationEvent {
  id?: string;
  _id?: string;
  ticketNo?: string;
  eventid?: string;
  eventId?: string;
  errorReason?: string;
  eventType?: string;
  datasource?: string;
  payloadstr?: string;
}

export function useReconciliation() {
  const events = ref<ReconciliationEvent[]>([]);
  const selectedEvent = ref<ReconciliationEvent | null>(null);
  const apiError: Ref<string | null> = ref(null);

  // Counts cache
  const counts = ref<Record<string, number>>({});

  const fetchEvents = async (card: any) => {
    const type = card.type;
    const cacheKey = `${StorageKey.EVENTS}_${type}`;

    const cached = storageType.getItem(cacheKey);
    if (cached) {
      try {
        events.value = JSON.parse(cached);
        selectedEvent.value = null;
        apiError.value = null;
        return;
      } catch (err) {
        console.warn(`Failed to parse cached data for type ${type}:`, err);
        storageType.removeItem(cacheKey); // clear invalid cache
      }
    }

    try {
      const response = await ReconService.fetchEvents(type);
      const data = response.data || [];

      events.value = data;
      selectedEvent.value = null;
      apiError.value = null;

      storageType.setItem(cacheKey, JSON.stringify(data)); // cache result

      
      const countCacheKey = `${StorageKey.EVENT_COUNT}_${type}`;
      storageType.removeItem(countCacheKey);
      // Refresh count after event fetch
      await fetchEventCount(card);
    } catch (err: any) {
      console.error('Error fetching events:', err);
      apiError.value = `Error calling API: ${err.response?.statusText || 'Unknown Error'}`;
    }
  };

  const fetchEventCount = async (card: any): Promise<number> => {
    const type = card.type;
    const countCacheKey = `${StorageKey.EVENT_COUNT}_${type}`;
    const cachedCount = storageType.getItem(countCacheKey);

    if (cachedCount !== null) {
      counts.value[type] = parseInt(cachedCount, 10);
      return counts.value[type];
    }

    try {
      const response = await ReconService.fetchCount(type);
      const count = response.data.count ?? 0;
      counts.value[type] = count;
      storageType.setItem(countCacheKey, count.toString()); // cache count
      return count;
    } catch (err: any) {
      console.error('Error fetching count:', err);
      counts.value[type] = 0;
      return 0;
    }
  };

  const selectEvent = (event: any) => {
    selectedEvent.value = event;
  };

  const refreshData = async (card: any) => {
    const eventCacheKey = `${StorageKey.EVENTS}_${card.type}`;
    const countCacheKey = `${StorageKey.EVENT_COUNT}_${card.type}`;

    storageType.removeItem(eventCacheKey);
    storageType.removeItem(countCacheKey);
    await fetchEvents(card);
    await fetchEventCount(card);
  };

  const parsedPayload = computed(() => {
    if (!selectedEvent.value || !selectedEvent.value.payloadstr) return '{}';

    let result = selectedEvent.value.payloadstr;
    try {
      result = JSON.parse(result);
      if (typeof result === 'string') {
        result = JSON.parse(result);
      }
      return JSON.stringify(result, null, 2);
    } catch (error) {
      console.error('Error parsing payload:', error);
      return selectedEvent.value.payloadstr;
    }
  });

  return {
    events,
    selectedEvent,
    apiError,
    counts,
    fetchEvents,
    fetchEventCount,
    selectEvent,
    refreshData,
    parsedPayload,
  };
}
