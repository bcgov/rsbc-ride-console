<script setup lang="ts"> 
import { ref, onMounted } from 'vue';
import { useFetchRecordsManager } from '@/composables/useFetchRecordsManager'; 
import GrafanaService from '@/services/grafanaService';

// Reconciliation metrics
const retryExceptions = ref(0);
const errorCount = ref(0);
const errorStaging = ref(0);
const stagingCount = ref(0);

// Error metrics
const newErrors = ref(0);
const underAnalysisCount = ref(0);

// Grafana iframe
const grafanaIframeUrl = ref('');
const dashboardUid = 'a6878b69-4a01-4cce-94b1-5747be221873';

// Composables
const reconManager = useFetchRecordsManager('reconciliation');
const errorManager = useFetchRecordsManager('error');

onMounted(async () => {
  // Reconciliation counts
  retryExceptions.value = await reconManager.fetchRecordCount({ type: 'retry-exceptions' });
  errorCount.value = await reconManager.fetchRecordCount({ type: 'error_count' });
  errorStaging.value = await reconManager.fetchRecordCount({ type: 'error_staging' });
  stagingCount.value = await reconManager.fetchRecordCount({ type: 'staging_count' });
  newErrors.value = await errorManager.fetchRecordCount({ type: 'new' });
  underAnalysisCount.value = await errorManager.fetchRecordCount({ type: 'under-analysis' });

  // Fetch fresh error records
  await errorManager.refreshData({ type: 'all' }); // Ensure no caching
  const allErrors = errorManager.records.value || [];

  // Grafana iframe
  try {
    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;
    grafanaIframeUrl.value = await GrafanaService.getDashboardEmbedUrl(
      dashboardUid, oneHourAgo, now
    );
  } catch (error) {
    console.error('Failed to load Grafana panel URL:', error);
  }
});
</script>

<template>
  <div class="home-tab-view">
    <h2 class="grafana-title">Services Status</h2>
    <div class="status-bar" v-if="grafanaIframeUrl">
      <iframe :src="grafanaIframeUrl" frameborder="0" allowfullscreen></iframe>
    </div>

    <div class="metrics-wrapper">
      <!-- Reconciliation Metrics -->
      <div class="metrics-container">
        <h2>Reconciliation metrics →</h2>
        <div class="metrics-cards">
          <div class="metric-card red">
            <div class="metric-number">{{ retryExceptions }}</div>
            <div class="metric-label">Retry Exceptions</div>
          </div>
          <div class="metric-card red">
            <div class="metric-number">{{ errorCount }}</div>
            <div class="metric-label">Error Count</div>
          </div>
          <div class="metric-card yellow">
            <div class="metric-number">{{ errorStaging }}</div>
            <div class="metric-label">Error Staging</div>
          </div>
          <div class="metric-card green">
            <div class="metric-number">{{ stagingCount }}</div>
            <div class="metric-label">Staging Count</div>
          </div>
        </div>
      </div>

      <!-- Errors Metrics -->
      <div class="metrics-container">
        <h2>Errors metrics →</h2>
        <div class="metrics-cards small-cards">
          <div class="metric-card small red">
            <div class="metric-number">{{ newErrors }}</div>
            <div class="metric-label">New errors</div>
          </div>
          <div class="metric-card small yellow">
            <div class="metric-number">{{ underAnalysisCount }}</div>
            <div class="metric-label">Under analysis</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-tab-view {
  padding: 1rem;
  font-family: Arial, sans-serif;
}

.status-bar {
  height: 160px;
  margin-bottom: 1.5rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.status-bar iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.metrics-wrapper {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 2rem;
}

.metrics-container {
  flex: 1 1 48%;
}

.metrics-container h2 {
  font-weight: 600;
  margin-bottom: 1rem;
}

.metrics-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: flex-start;
}

/* Reconciliation cards */
.metric-card {
  flex: 1 1 110px;
  border-radius: 12px;
  padding: 0.75rem;
  text-align: center;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
  user-select: none;
  min-width: 110px;
}

/* Error cards smaller width */
.metrics-cards.small-cards .metric-card.small {
  flex: 1 1 90px;
  min-width: 90px;
}

.metric-number {
  font-size: 2.25rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-weight: 600;
  font-size: 0.95rem;
}

.metric-card.red {
  background-color: #f9c2c2;
  color: #9b1c1c;
}

.metric-card.yellow {
  background-color: #f9e6a0;
  color: #9b7c1c;
}

.metric-card.green {
  background-color: #c3e9c4;
  color: #2f7d32;
}


</style>
