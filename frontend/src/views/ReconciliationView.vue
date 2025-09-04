<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import SidebarTab from '@/components/layout/SidebarTab.vue';
import { useFetchRecordsManager } from '@/composables/useFetchRecordsManager';
import {useReconUpdater} from '@/composables/useReconUpdater';
import ProducerService from '@/services/producerService';
import { StorageKey } from '@/utils/constants';
import FetchRecordsService from '@/services/fetchRecordsService';


const service = FetchRecordsService;
const storageType = window.sessionStorage;



// Filters
const filters = ref({
  ticketNo: '',
  eventId: '',
  errorReason: '',
  eventType: '',
  datasource: '',
});

// Tabs
const cards = ref([
  { title: 'Retry Exceptions ', type: 'retry-exceptions', class: 'red', count: 0 },
  { title: 'Error Count', type: 'error_count', class: 'darkred', count: 0 },
  { title: 'Error Staging', type: 'error_staging', class: 'orange', count: 0 },
  { title: 'Staging Count', type: 'staging_count', class: 'green', count: 0 },
]);

const activeCard = ref(cards.value[0]);

const {
  records,
  selectedRecord,
  apiError,
  fetchRecords,
  fetchRecordCount,
  selectRecord,
  refreshData,
  parsedPayload
} = useFetchRecordsManager('reconciliation');

const {
  resetAllByType,
  resetById,
  deleteEventById,
  deleteAllEvents
} = useReconUpdater();

onMounted(async () => {
  for (const card of cards.value) {
    card.count = await fetchRecordCount(card);
  }
  await fetchRecords(activeCard.value);
});

const filteredRecords = computed(() => {
  return records.value.filter(record => {
    const matches = (fieldValue: any, filterValue: string) => {
      if (!filterValue) return true;
      if (!fieldValue) return false;
      return fieldValue.toString().toLowerCase().includes(filterValue.toLowerCase());
    };

    return (
      matches(record.ticketNo, filters.value.ticketNo) &&
      matches(record.eventid || record.eventId, filters.value.eventId) &&
      matches(record.errorReason, filters.value.errorReason) &&
      matches(record.eventType, filters.value.eventType) &&
      matches(record.datasource, filters.value.datasource)
    );
  });
});

watch(filters, () => {
  selectedRecord.value = null;
}, { deep: true });

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(val => val.trim() !== '');
});

function onSelectRecord(record: any) {
  selectRecord(record);
  menuOpen.value = false;
  detailMenuOpen.value = false;
}

// Menu toggle
const menuOpen = ref(false);
const toggleMenu = () => {
  menuOpen.value = !menuOpen.value;
};

// Tab checks
const isRetryTab = computed(() => activeCard.value.type === 'retry-exceptions');
const isErrorCountTab = computed(() => activeCard.value.type === 'error_count');

// Refresh counts for all tabs
async function refreshAllCounts() {
  for (const card of cards.value) {
    storageType.removeItem(`${StorageKey.EVENT_COUNT}_error_${card.type}`);
    card.count = await fetchRecordCount(card);
  }
}

const resetRetryCount = async () => {
  if (!selectedRecord.value) return;
  try {
    await resetById(activeCard.value.type ?? '', selectedRecord.value._id ?? '');
    refreshAllData();
  } catch (e) {
    console.error('Error resetting retry count', e);
  }
};

const resubmitToProducer = async () => {
  if (!selectedRecord.value || !parsedPayload.value) return;

  const apiPath = selectedRecord.value.apipath ?? '';
  if (!apiPath) {
    alert('No API path specified for this record.');
    return;
  }

  const confirmResubmit = window.confirm('Are you sure you want to resubmit this event to the producer?');
  if (!confirmResubmit) return;

  try {
    let payloadToSend = parsedPayload.value;
    if (typeof payloadToSend === 'string') {
      try {
        payloadToSend = JSON.parse(payloadToSend);
      } catch (e) {
        console.error('Failed to parse payload string', e);
        alert('Invalid JSON format in payload');
        return;
      }
    }

    // Ensure payload is an object and not null
    if (!payloadToSend || typeof payloadToSend !== 'object') {
      alert('Payload must be a valid object to send.');
      return;
    }

    await ProducerService.send(apiPath, payloadToSend);
    alert('Payload successfully sent to producer.');
  } catch (error) {
    alert('Failed to send payload to producer.');
    console.error(error);
  }
};


const resubmitAllToProducer = async () => {
  if (!records.value.length) {
    alert('No records to resubmit.');
    return;
  }

  const confirmResubmit = window.confirm(`Are you sure you want to resubmit all ${records.value.length} events to the producer?`);
  if (!confirmResubmit) return;

  for (const record of records.value) {
    try {
      const apiPath = record.apipath ?? '';
      if (!apiPath) {
        console.warn(`Skipping record ${record._id} — no API path.`);
        continue;
      }

      
      let payloadToSend: any = record.payload ?? parsedPayload.value; // fallback to parsedPayload if no per-record payload
      
      
      if (typeof payloadToSend === 'string') {
        try {
          payloadToSend = JSON.parse(payloadToSend);
        } catch (e) {
          console.error(`Failed to parse payload for record ${record._id}`, e);
          continue; // skip this record and continue with others
        }
      }

      
      if (!payloadToSend || typeof payloadToSend !== 'object') {
        console.warn(`Skipping record ${record._id} — invalid payload`);
        continue;
      }

      await ProducerService.send(apiPath, payloadToSend);
    } catch (error) {
      console.error(`Failed to resubmit record ${record._id}`, error);
    }
  }

  alert('Finished resubmitting all events.');
};

const resetAllHandler = async () => {
  await resetAllByType(activeCard.value.type);  
  refreshAllData();
  menuOpen.value = false;
};

const retryExceptionsCount = computed(() => {
  const card = cards.value.find(c => c.type === 'retry-exceptions');
  return card ? card.count : 0;
});

const refreshAllData = async () => {
  // Refresh counts for all tabs
  for (const card of cards.value) {
    storageType.removeItem(`${StorageKey.EVENT_COUNT}_reconciliation_${card.type ?? 'unknown'}`);
    card.count = await fetchRecordCount(card);
  }

  // Refresh and cache data for all tabs (including inactive)
  for (const card of cards.value) {
    const response = await service.fetchRecords('reconciliation', card.type);
    const data = response.data || [];
    storageType.setItem(`${StorageKey.EVENTS}_${'reconciliation'}_${card.type}`, JSON.stringify(data));
  }

  // Finally, load active tab's data into UI
  await fetchRecords(activeCard.value);
};



const detailMenuOpen = ref(false);

const toggleDetailMenu = () => {
  detailMenuOpen.value = !detailMenuOpen.value;
};

const deleteSelectedEvent = async () => {
  if (!selectedRecord.value) return;
  const confirmDelete = window.confirm('Are you sure you want to delete this event?');
  if (!confirmDelete) return;
  try {
    await deleteEventById(activeCard.value.type  ?? '', selectedRecord.value._id  ?? '');
    alert('Event deleted successfully.');
    selectedRecord.value = null; // clear selection after deletion
    refreshAllData();
    
  } catch (error) {
    console.error('Failed to delete event:', error);
    alert('Failed to delete event.');
  }
};

</script>

<template>
  <div class="reconciliation-view">
    <!-- Header -->
    <div class="top-bar">
      <div class="top-bar-left">
        <button class="refresh-button" @click="refreshAllData">
          Refresh
        </button>
        <div class="filters">
          <input v-model="filters.ticketNo" placeholder="Ticket no." />
          <input v-model="filters.eventId" placeholder="Event ID" />
          <input v-model="filters.errorReason" placeholder="Error Reason" />
          <input v-model="filters.eventType" placeholder="Event Type" />
          <input v-model="filters.datasource" placeholder="Data Source" />
        </div>
      </div>

      <!-- 3-dot menu -->
      <div class="menu-button">
        <span class="material-icons" @click="toggleMenu" >more_vert</span>
        <div v-if="menuOpen" class="menu">
          <button  @click="resubmitAllToProducer">  Resubmit all to Producer</button>

          <button  @click="resetAllHandler">
            <!-- Label changes depending on tab -->
            <template v-if="isRetryTab">Reset all recon count</template>
            <template v-else>Reset all retry count</template>
          </button>

          <button disabled>Delete all</button>
        
        </div>
      </div>
    </div>

    <!-- Main layout -->
    <div class="main-container">
      <!-- Sidebar Tabs -->
      <div class="sidebar">
        <SidebarTab
          v-for="card in cards"
          :key="card.title"
          :tab="card"
          :isActive="activeCard === card"
          @click="(clickedTab) => { activeCard = clickedTab; fetchRecords(clickedTab); menuOpen = false }"
        />
      </div>

      <!-- Record list -->
      <div class="record-list-container">
        <div v-if="apiError" class="error-message">
          <p>{{ apiError }}</p>
        </div>

        <div v-else-if="filteredRecords.length === 0 && hasActiveFilters" class="no-results">
          No matching records found.
        </div>

        <div
          v-for="record in filteredRecords"
          :key="record._id"
          class="record-list-item"
          @click="onSelectRecord(record)"
        >
          <div class="item-title">
            <strong>{{ record.errorReason || '<Error Reason Unknown>' }}</strong>
          </div>
          <div class="item-subtext">{{ record.eventType || '-' }}</div>
          <div class="item-subtext">{{ record.datasource || '-' }}</div>
          <div class="arrow">›</div>
        </div>
      </div>

      <!-- Record Details -->
      <div class="record-details" v-if="selectedRecord">
          <div class="detail-menu-button">
            <span class="material-icons" @click="toggleDetailMenu">more_vert</span>
            <div v-if="detailMenuOpen" class="detail-menu">
              <button @click="resubmitToProducer" >Resubmit to Producer</button>
              <button  @click="resetRetryCount">Reset retry count</button>
              <button  @click="deleteSelectedEvent" >Delete</button>
            </div>
         </div>
        <h3>{{ selectedRecord.errorReason || '< Error Reason Unknown>' }}</h3>
        <p>{{ selectedRecord.eventType }}</p>
        <p><strong>Event ID:</strong> {{ selectedRecord.eventid }}</p>
        <p><strong>Object ID:</strong> {{ selectedRecord._id }}</p>
        <p><strong>API Path:</strong> {{ selectedRecord.apipath }}</p>

        <div class="payload">
          <strong>Payload</strong>
          <pre>{{ parsedPayload }}</pre>
        </div>

        <div class="record-actions"/>
      
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

.reconciliation-view {
  font-family: sans-serif;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f9f9f9;
}
.material-icons {
  font-size: 24px;
  cursor: pointer;
  color: #555;
}
.menu {
  position: absolute;
  top: 28px;
  right: 0;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  z-index: 1000;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.menu button {
  padding: 10px 16px;
  background: none;
  border: none;
  width: 220px;
  text-align: left;
  cursor: pointer;
}
.menu button:disabled {
  color: #aaa;
  cursor: not-allowed;
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
.record-actions {
  margin-top: 20px;
}
.record-actions button {
  padding: 10px 20px;
  background-color: #c72a2a;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}
.record-actions button:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}
.record-actions button:hover:not(:disabled) {
  background-color: #a12424;
}
.top-bar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.refresh-button {
  padding: 8px 14px;
  background-color: #3498db;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}
.refresh-button:hover {
  background-color: #2c80b4;
}
.top-bar-left {
  display: flex;
  align-items: center;
  gap: 16px; /* space between refresh button and filters */
  flex: 1;
}
.detail-menu-button {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 10;
}
.detail-menu-button .material-icons {
  font-size: 24px;
  cursor: pointer;
  color: #6c5ce7;
}
.detail-menu {
  position: absolute;
  top: 32px;
  right: 0;
  background: #f5edf7;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  z-index: 1000;
}
.detail-menu button {
  display: block;
  padding: 10px 16px;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  color: #333;
}
.detail-menu button:hover:not(:disabled) {
  background-color: #f0dff9;
}
.detail-menu button:disabled {
  color: #aaa;
  cursor: not-allowed;
}
.global-menu-container {
  position: relative;
}
.menu-button {
  position: relative;
  margin-left: 100px; 
}
.top-bar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
