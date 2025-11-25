<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import GrafanaService from '@/services/grafanaService';

/* --------------------------------------------
   SYSTEM PERFORMANCE PANELS
-------------------------------------------- */
const cpuPanelUrl = ref('');
const memoryPanelUrl = ref('');
const storagePanelUrl = ref('');

/* --------------------------------------------
   API COMPONENT PANELS
-------------------------------------------- */
const availableApisPanelUrl = ref('');
const unavailableApisPanelUrl = ref('');
const apiNetworkErrorsUrl = ref('');
const apiHttpNetworkErrorsUrl = ref('');
const apiLatencyUrl = ref('');

/* --------------------------------------------
   TIME RANGE CONFIG
-------------------------------------------- */
const timeRanges = [
  { label: 'Last Hour', value: 1 },
  { label: 'Last 6 Hours', value: 6 },
  { label: 'Last 24 Hours', value: 24 }
];

// System Performance time range
const selectedRange = ref(24);

// API Components time range
const selectedApiRange = ref(24);

/* --------------------------------------------
   LOAD SYSTEM PANELS
-------------------------------------------- */
async function loadSystemPanels() {
  try {
    const to = Date.now();
    const from = to - selectedRange.value * 60 * 60 * 1000;

    cpuPanelUrl.value = await GrafanaService.getCpuUsagePanelUrl(from, to);
    memoryPanelUrl.value = await GrafanaService.getMemoryUsagePanelUrl(from, to);
    storagePanelUrl.value = await GrafanaService.getStorageUsagePanelUrl(from, to);
  } catch (err) {
    console.error('Failed to load system panels:', err);
  }
}

/* --------------------------------------------
   LOAD API PANELS
-------------------------------------------- */
async function loadApiPanels() {
  try {
    const to = Date.now();
    const from = to - selectedApiRange.value * 60 * 60 * 1000;

    availableApisPanelUrl.value = await GrafanaService.getAvailableAPIsPanelUrl(from, to);
    unavailableApisPanelUrl.value = await GrafanaService.getUnavailableAPIsPanelUrl(from, to);
    apiNetworkErrorsUrl.value = await GrafanaService.getAPINetWorkErrorsPanelUrl(from, to);
    apiHttpNetworkErrorsUrl.value = await GrafanaService.getAPIHTTPNetWorkErrorsPanelUrl(from, to);
    apiLatencyUrl.value = await GrafanaService.getAPILatencyPanelUrl(from, to);
  } catch (err) {
    console.error('Failed to load API panels:', err);
  }
}

// Initial load
onMounted(() => {
  loadSystemPanels();
  loadApiPanels();
});

// Watch for time range changes
watch(selectedRange, loadSystemPanels);
watch(selectedApiRange, loadApiPanels);
</script>

<template>
  <div class="dashboards-view">

    <!-- -----------------------------------------------------------
         SECTION 1: SYSTEM PERFORMANCE OVERVIEW
    ------------------------------------------------------------ -->
    <div class="dashboard-header">
      <h2 class="dashboard-title">System Performance Overview</h2>

      <select v-model="selectedRange" class="time-range-select">
        <option v-for="range in timeRanges" :key="range.value" :value="range.value">
          {{ range.label }}
        </option>
      </select>
    </div>

    <div class="dashboard-panels">
      <div class="dashboard-panel" v-if="cpuPanelUrl">
        <h3>CPU Usage Overview</h3>
        <iframe :src="cpuPanelUrl" />
      </div>

      <div class="dashboard-panel" v-if="memoryPanelUrl">
        <h3>Memory Usage Overview</h3>
        <iframe :src="memoryPanelUrl" />
      </div>

      <div class="dashboard-panel" v-if="storagePanelUrl">
        <h3>Storage Usage Overview</h3>
        <iframe :src="storagePanelUrl" />
      </div>
    </div>

    <!-- -----------------------------------------------------------
         SECTION 2: API COMPONENTS
    ------------------------------------------------------------ -->
    <div class="dashboard-header api-header">
      <h2 class="dashboard-title">API Components</h2>

      <select v-model="selectedApiRange" class="time-range-select">
        <option v-for="range in timeRanges" :key="range.value" :value="range.value">
          {{ range.label }}
        </option>
      </select>
    </div>

    <div class="dashboard-panels">

      <div class="dashboard-panel" v-if="availableApisPanelUrl">
        <h3>Available APIs</h3>
        <iframe :src="availableApisPanelUrl" />
      </div>

      <div class="dashboard-panel" v-if="unavailableApisPanelUrl">
        <h3>Unavailable APIs</h3>
        <iframe :src="unavailableApisPanelUrl" />
      </div>

      <div class="dashboard-panel" v-if="apiNetworkErrorsUrl">
        <h3>API Network Errors</h3>
        <iframe :src="apiNetworkErrorsUrl" />
      </div>

      <div class="dashboard-panel" v-if="apiHttpNetworkErrorsUrl">
        <h3>API HTTP Network Errors</h3>
        <iframe :src="apiHttpNetworkErrorsUrl" />
      </div>

      <div class="dashboard-panel" v-if="apiLatencyUrl">
        <h3>API Latency</h3>
        <iframe :src="apiLatencyUrl" />
      </div>

    </div>

  </div>
</template>

<style scoped>
.dashboards-view {
  padding: 1.5rem;
  font-family: Arial, sans-serif;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  margin-top: 20px;
}

.api-header {
  margin-top: 2.5rem;
}

/* Title */
.dashboard-title {
  font-weight: 600;
  margin: 0;
}

/* Dropdown styling */
.time-range-select {
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #fff;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}
.time-range-select:hover {
  border-color: #888;
}

/* Panels */
.dashboard-panels {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.dashboard-panel {
  flex: 1 1 30%;
  min-width: 350px;
  background-color: #fafafa;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.dashboard-panel h3 {
  padding: 0.75rem 1rem;
  background-color: #f3f4f6;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.dashboard-panel iframe {
  width: 100%;
  height: 300px;
  border: none;
}
</style>
