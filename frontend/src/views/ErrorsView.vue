<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import SidebarTab from '@/components/layout/SidebarTab.vue';
import { useFetchRecordsManager } from '@/composables/useFetchRecordsManager';
import { useErrorUpdater } from '@/composables/useErrorUpdater';
import { StorageKey } from '@/utils/constants';

import FetchRecordsService from '@/services/fetchRecordsService';


const service = FetchRecordsService;
const storageType = window.sessionStorage;


const filters = ref({
  ticketNo: '',
  severity: '',
  category: '',
  eventId: '',
});

const cards = ref([
  { title: 'New errors', type: 'new', class: 'red', count: 0 },
  { title: 'Under analysis', type: 'under-analysis', class: 'orange', count: 0 },
  { title: 'Fixed', type: 'fixed', class: 'green', count: 0 },
]);

const {
  records,
  selectedRecord,
  apiError,
  fetchRecords,
  fetchRecordCount,
  selectRecord,
  refreshData,
} = useFetchRecordsManager('error');

const {
  setFixedById,
  setUnderAnalysisById,
  setAllFixed,
  setAllUnderAnalysis,
} = useErrorUpdater();

const activeCard = ref(cards.value[0]);

const recordMenuOpenFor = ref<string | null>(null);
const globalMenuOpen = ref(false);
const isRefreshing = ref(false);

const refreshAllData = async () => {
  // Refresh counts for all tabs
  for (const card of cards.value) {
    storageType.removeItem(`${StorageKey.EVENT_COUNT}_error_${card.type}`);
    card.count = await fetchRecordCount(card);
  }

  // Refresh and cache data for all tabs (including inactive)
  for (const card of cards.value) {
    const response = await service.fetchRecords('error', card.type);
    const data = response.data || [];
    storageType.setItem(`${StorageKey.EVENTS}_${'error'}_${card.type}`, JSON.stringify(data));
  }

  // Finally, load active tab's data into UI
  await fetchRecords(activeCard.value);
};



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
      matches(record.errorSeverityLevelCd, filters.value.severity) &&
      matches(record.errorCategoryCd, filters.value.category) &&
      matches(record._id, filters.value.eventId)
    );
  });
});

watch(filters, () => {
  selectedRecord.value = null;
}, { deep: true });

const hasActiveFilters = computed(() =>
  Object.values(filters.value).some(val => val.trim() !== '')
);

const openRecordMenu = (recordId: string) => {
  recordMenuOpenFor.value = recordMenuOpenFor.value === recordId ? null : recordId;
};

const closeRecordMenu = () => {
  recordMenuOpenFor.value = null;
};

const toggleGlobalMenu = () => {
  globalMenuOpen.value = !globalMenuOpen.value;
};

const closeGlobalMenu = () => {
  globalMenuOpen.value = false;
};

const handleSetFixed = async (recordId: string) => {
  if (!activeCard.value) return;
  await setFixedById(activeCard.value.type, recordId);  
  refreshAllData();
  closeRecordMenu();
};

const handleSetUnderAnalysis = async (recordId: string) => {
  if (!activeCard.value) return;
  await setUnderAnalysisById(activeCard.value.type, recordId);
  refreshAllData(); 
 
  closeRecordMenu();
};

const handleSetAllFixed = async () => {
  if (!activeCard.value) return;
  const updatePromises = filteredRecords.value.map(record =>
    setFixedById(activeCard.value.type, record._id || '')
  );
  await Promise.all(updatePromises);
  await refreshAllData();
  closeGlobalMenu();
};

const handleSetAllUnderAnalysis = async () => {
  if (!activeCard.value) return;
  const updatePromises = filteredRecords.value.map(record =>
    setUnderAnalysisById(activeCard.value.type, record._id || '')
  );
  await Promise.all(updatePromises);
  await refreshAllData();
  closeGlobalMenu();
};

const isFixedTab = computed(() => activeCard.value.type === 'fixed');
const isUnderAnalysisTab = computed(() => activeCard.value.type === 'under-analysis');



</script>

<template>
  <div class="error-view">
    <!-- Filters -->
    <div class="filters">
      <input v-model="filters.ticketNo" placeholder="Ticket no." />
      <input v-model="filters.severity" placeholder="Severity" />
      <input v-model="filters.category" placeholder="Category" />
      <input v-model="filters.eventId" placeholder="Event ID" />

      <!-- Global menu moved here -->
      <div class="global-menu-container" @click.stop="toggleGlobalMenu" style="margin-left: auto;">
        <button class="menu-trigger" aria-label="More options">⋮</button>
        <div v-if="globalMenuOpen" class="menu-dropdown" @click.stop>
          <button
              class="menu-button"
              @click="handleSetAllUnderAnalysis"
              v-if="!isUnderAnalysisTab"
            >
              Set all under analysis
            </button>
            <button
              class="menu-button"
              @click="handleSetAllFixed"
              v-if="!isFixedTab"
            >
              Set all fixed
          </button>
        </div>
      </div>
    </div>

    <!-- Refresh button -->
    <div class="refresh-container">
      <button @click="refreshAllData" :disabled="isRefreshing">
        {{ isRefreshing ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- Layout -->
    <div class="main-container">
      <!-- Left sidebar -->
      <div class="sidebar">
        <SidebarTab
          v-for="card in cards"
          :key="card.title"
          :tab="card"
          :isActive="activeCard === card"
          @click="(clickedTab) => {
            activeCard = clickedTab;
            fetchRecords(card);            
            closeRecordMenu();
            closeGlobalMenu();
          }"
        />

      </div>

      <!-- Record list -->
      <div class="record-list-container">
        <div v-if="apiError" class="error-message">{{ apiError }}</div>

        <div v-else-if="filteredRecords.length === 0 && hasActiveFilters" class="no-results">
          No matching errors found.
        </div>

        <div
          v-for="record in filteredRecords"
          :key="record._id"
          class="record-list-item"
          @click="selectRecord(record)"
        >
          <div class="item-title">
            <strong>{{ record.detailsTxt }}</strong>
          </div>

          <div class="item-subtext">{{ record.errorCategoryCd || '-' }}</div>
          <div class="item-subtext">Event ID: {{ record._id }}</div>
          <div class="item-subtext">Ticket No: {{ record.ticketNo }}</div>
          <div class="item-subtext">Severity: {{ record.errorSeverityLevelCd || '-' }}</div>
          <div class="item-subtext" v-if="record.comments && record.comments[0]?.date">
            Date: {{ new Date(record.comments[0].date).toLocaleString() }}
          </div>
          <div class="arrow">›</div>
        </div>
      </div>

      <!-- Detail view -->
      <div class="record-details" v-if="selectedRecord" style="position: relative;">
        <!-- Individual record menu positioned top-right -->
        <div
          class="record-menu-container"
          @click.stop="openRecordMenu(selectedRecord._id || '')"
          style="position: absolute; top: 10px; right: 10px;"
        >
          <button class="menu-trigger" aria-label="More options">⋮</button>
          <div v-if="recordMenuOpenFor === selectedRecord._id" class="menu-dropdown" @click.stop>
             <button v-if="!isUnderAnalysisTab" class="menu-button" @click="handleSetUnderAnalysis(selectedRecord._id)">
              Under analysis
            </button>
            <button   v-if="!isFixedTab" class="menu-button" @click="handleSetFixed(selectedRecord._id)">
              Fixed
            </button>
          </div>
        </div>

        <h3>{{ selectedRecord.detailsTxt }}</h3>
        <p><strong>Category:</strong> {{ selectedRecord.errorCategoryCd }}</p>
        <p><strong>Event ID:</strong> {{ selectedRecord._id }}</p>
        <p><strong>Error ID:</strong> {{ selectedRecord.ticketNo }}</p>
        <p><strong>Severity:</strong> {{ selectedRecord.errorSeverityLevelCd }}</p>
        <p>
          <strong>Error details:</strong>
          {{
            selectedRecord.comments && selectedRecord.comments.length > 0
              ? selectedRecord.comments[0].comment
              : '<No comment>'
          }}
        </p>
        <p>
          <strong>Error Path:</strong>
          {{ selectedRecord.serviceNm }}
          {{ selectedRecord._class ? ' : .' + selectedRecord._class + ' /' : ' /' }}
        </p>

        <div class="payload" v-if="selectedRecord.comments && selectedRecord.comments.length > 0">
          <strong>Payload</strong>
          <pre>{{ JSON.stringify(selectedRecord.comments[0], null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.error-view {
  font-family: sans-serif;
  display: flex;
  flex-direction: column;
  height: 100vh;
}




.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background-color: #fff8fc;
  border-right: 1px solid #ddd;
  padding: 10px;
  position: relative;
}

.global-menu-container {
  position: relative;
}


</style>
