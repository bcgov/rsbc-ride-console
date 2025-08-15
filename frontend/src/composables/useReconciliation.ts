import { ref, computed } from 'vue';
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

  // 🟢 Fetch events from API (with caching)
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
    } catch (err: any) {
      console.error('Error:', err);
      apiError.value = `Error calling API: ${err.response?.statusText || 'Unknown Error'}`;
    }
  };

  // 🟢 Fetch count for a given card type
  const fetchEventCount = async (card: any): Promise<number> => {
    try {
      const response = await ReconService.fetchCount(card.type);
      return response.data.count || 0;
    } catch (err: any) {
      console.error('Error fetching count:', err);
      return 0;
    }
  };

  const selectEvent = (event: any) => {
    selectedEvent.value = event;
  };

  const refreshData = async (card: any) => {
    const key = `${StorageKey.EVENTS}_${card.type}`;
    storageType.removeItem(key);
    await fetchEvents(card);
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
    fetchEvents,
    fetchEventCount, // <-- 🟢 expose count fetching
    selectEvent,
    refreshData,
    parsedPayload,
  };
}
