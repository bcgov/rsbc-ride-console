<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import ReconService from '@/services/reconService';
import EventListItem from '@/components/layout/EventListItem.vue';
import SidebarTab from '@/components/layout/ReconSidebarTab.vue';
import { useReconciliation } from '@/composables/useReconciliation';

// Filters
const filters = ref({
  ticketNo: '',
  eventId: '',
  errorReason: '',
  eventType: '',
  datasource: '',
});

// Tabs (cards)
const cards = ref([
  { title: 'Retry Exceptions', type: 'retry-exceptions', class: 'red', count: 0 },
  { title: 'Error Count', type: 'error_count', class: 'darkred', count: 0 },
  { title: 'Error Staging', type: 'error_staging', class: 'orange', count: 0 },
  { title: 'Staging Count', type: 'staging_count', class: 'green', count: 0 },
]);

// Composable logic
const {
  events,
  selectedEvent,
  apiError,
  fetchEvents,
  fetchEventCount,
  selectEvent,
  parsedPayload,
} = useReconciliation();

// Fetch counts for each card on mount
onMounted(async () => {
  for (const card of cards.value) {
    card.count = await fetchEventCount(card);
  }
});

// Filtered events based on search filters
const filteredEvents = computed(() => {
  return events.value.filter(event => {
    const matches = (fieldValue: any, filterValue: string) => {
      if (!filterValue) return true;
      if (!fieldValue) return false;
      return fieldValue.toString().toLowerCase().includes(filterValue.toLowerCase());
    };

    return (
      matches(event.ticketNo, filters.value.ticketNo) &&
      matches(event.eventid || event.eventId, filters.value.eventId) &&
      matches(event.errorReason, filters.value.errorReason) &&
      matches(event.eventType, filters.value.eventType) &&
      matches(event.datasource, filters.value.datasource)
    );
  });
});
</script>

<template>
  <div class="reconciliation-view">
    <!-- Top Filters -->
    <div class="filters">
      <input v-model="filters.ticketNo" placeholder="Ticket no." />
      <input v-model="filters.eventId" placeholder="Event ID" />
      <input v-model="filters.errorReason" placeholder="Error Reason" />
      <input v-model="filters.eventType" placeholder="Event Type" />
      <input v-model="filters.datasource" placeholder="Data Source" />
    </div>

    <!-- Main Layout -->
    <div class="main-container">
      <!-- Sidebar -->
      <div class="sidebar">
        <SidebarTab
          v-for="card in cards"
          :key="card.title"
          :tab="card"
          @click="fetchEvents(card)"
        />
      </div>

      <!-- Event List -->
      <div class="event-list-container">
        <div v-if="apiError" class="error-message">
          <p>{{ apiError }}</p>
        </div>

        <EventListItem
          v-for="event in filteredEvents"
          :key="event._id"
          :event="event"
          @select="selectEvent"
        />
      </div>

      <!-- Event Detail -->
      <div class="event-details" v-if="selectedEvent">
        <h3>{{ selectedEvent.errorReason || '< Error Reason Unknown>' }}</h3>
        <p>{{ selectedEvent.eventType }}</p>
        <p><strong>Event ID:</strong> {{ selectedEvent.eventid }}</p>
        <p><strong>Object ID:</strong> {{ selectedEvent._id }}</p>

        <div class="payload">
          <strong>Payload</strong>
          <pre>{{ parsedPayload }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reconciliation-view {
  font-family: sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.filters {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: #f9f9f9;
}

.filters input {
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #ccc;
  flex: 1;
  min-width: 150px;
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 180px;
  background-color: #fff8fc;
  border-right: 1px solid #ddd;
  padding: 10px;
}

.event-list-container {
  width: 300px;
  background-color: #fdf7ff;
  border-right: 1px solid #ddd;
  overflow-y: auto;
  padding: 10px;
}

.event-details {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.payload pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 5px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 10px;
}
</style>
