<script setup lang="ts">
import { ref } from 'vue';
import ReconciliationView from './ReconciliationView.vue';
import HomeSidebar from '@/components/layout/HomeSidebar.vue';


const activeTab = ref('Reconciliation');

const tabs = [
  { name: 'Home', label: 'Home', icon: 'home' },
  { name: 'Reconciliation', label: 'Recon', icon: 'star' },
  { name: 'Dashboards', label: 'Dashboards', icon: 'pie_chart' },
  { name: 'PrimeFTP', label: 'Prime FTP', icon: 'folder' },
  { name: 'Errors', label: 'Errors', icon: 'error' },
];

function setActiveTab(tabName: string) {
  activeTab.value = tabName;
}
</script>

<template>
  <div class="home-view">
    <!-- Sidebar -->
    <HomeSidebar
      :tabs="tabs"
      :activeTab="activeTab"
      @tab-click="setActiveTab"
    />

    <!-- Main content -->
    <div class="content">
      <ReconciliationView v-if="activeTab === 'Reconciliation'" />
      <div v-if="activeTab === 'Home'">
        <h2>Welcome to Home</h2>
      </div>
      <div v-if="activeTab === 'Dashboards'">
        <h2>Dashboard Content</h2>
      </div>
      <div v-if="activeTab === 'PrimeFTP'">
        <h2>Prime FTP Content</h2>
      </div>
      <div v-if="activeTab === 'Errors'">
        <h2>Error Logs or Management</h2>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  height: 100vh;
}

/* Sidebar styles */
.sidebar {
  width: 80px;
  background-color: #fef7ff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  border-right: 1px solid #e0e0e0;
}

/* Sidebar item */
.sidebar-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
  cursor: pointer;
  color: #555;
  font-size: 12px;
  transition: color 0.2s ease;
}

.sidebar-tab:hover {
  color: #222;
}

.sidebar-tab.active {
  font-weight: bold;
  color: #000;
}

.icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  transition: background-color 0.3s;
}

.icon-wrapper.selected {
  background-color: #ede7f6; /* light purple */
}

/* Icon size and alignment */
.material-icons {
  font-size: 24px;
}

/* Main content area */
.content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}
</style>
