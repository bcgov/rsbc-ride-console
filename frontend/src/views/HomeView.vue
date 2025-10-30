<script setup lang="ts">
import { ref } from 'vue';
import ReconciliationView from './ReconciliationView.vue';
import ErrorsView from './ErrorsView.vue';
import FtpView from './FtpView.vue';
import DashboardsView from './DashboardsView.vue';

import HomeTabView  from './HomeTabView.vue';
import HomeSidebar from '@/components/layout/HomeSidebar.vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/store';
const { getIsAuthenticated } = storeToRefs(useAuthStore());


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
  <div   v-if="getIsAuthenticated" class="home-view">
    <!-- Sidebar -->
    <HomeSidebar
      :tabs="tabs"
      :activeTab="activeTab"
      @tab-click="setActiveTab"
    />

    <!-- Main content -->
    <div class="content">
      <ReconciliationView v-if="activeTab === 'Reconciliation'" />
      <HomeTabView v-if="activeTab === 'Home'" />
      <FtpView v-if="activeTab === 'PrimeFTP'" />
      <ErrorsView v-if="activeTab === 'Errors'" />
      <DashboardsView v-if="activeTab === 'Dashboards'" />
      
      
    </div>
  </div>
   <!-- 👋 Default welcome screen for unauthenticated users -->
<div v-else class="p-8">
  <div class="text-center">
    <h1 class="text-4xl font-bold mb-6">Welcome to the RIDE Console!</h1>
    </div>

  </div>


</template>

<style scoped>
.home-view {
  display: flex;
  height: 100vh;
}

.content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}



</style>
