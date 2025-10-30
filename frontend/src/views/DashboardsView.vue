<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import GrafanaService from '@/services/grafanaService';

// Panel URLs
const cpuPanelUrl = ref('');
const memoryPanelUrl = ref('');
const storagePanelUrl = ref('');

// Time range options
const timeRanges = [
  { label: 'Last Hour', value: 1 },
  { label: 'Last 6 Hours', value: 6 },
  { label: 'Last 24 Hours', value: 24 },
];

// Default time range (in hours)
const selectedRange = ref(24);

async function loadPanels() {
  try {
    const to = Date.now();
    const from = to - selectedRange.value * 60 * 60 * 1000; // dynamic range

    cpuPanelUrl.value = await GrafanaService.getCpuUsagePanelUrl(from, to);
    memoryPanelUrl.value = await GrafanaService.getMemoryUsagePanelUrl(from, to);
    storagePanelUrl.value = await GrafanaService.getStorageUsagePanelUrl(from, to);
  } catch (err) {
    console.error('Failed to load Grafana panels:', err);
  }
}

// Load panels initially and whenever the user changes the time range
onMounted(loadPanels);
watch(selectedRange, loadPanels);
</script>

<template>
  <div class="dashboards-view">
    <div class="dashboard-header">
      <h2 class="dashboard-title">System Performance Overview</h2>

      <!-- ⏱️ Time range dropdown -->
      <select v-model="selectedRange" class="time-range-select">
        <option v-for="range in timeRanges" :key="range.value" :value="range.value">
          {{ range.label }}
        </option>
      </select>
    </div>

    <div class="dashboard-panels">
      <div class="dashboard-panel" v-if="cpuPanelUrl">
        <h3>CPU Usage Overview</h3>
        <iframe :src="cpuPanelUrl" frameborder="0" allowfullscreen/>
      </div>

      <div class="dashboard-panel" v-if="memoryPanelUrl">
        <h3>Memory Usage Overview</h3>
        <iframe :src="memoryPanelUrl" frameborder="0" allowfullscreen/>
      </div>

      <div class="dashboard-panel" v-if="storagePanelUrl">
        <h3>Storage Usage Overview</h3>
        <iframe :src="storagePanelUrl" frameborder="0" allowfullscreen/>
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
}

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

/* Panels grid */
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
