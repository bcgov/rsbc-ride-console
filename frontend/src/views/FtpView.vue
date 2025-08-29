<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import SidebarTab from '@/components/layout/SidebarTab.vue';
import { useFetchRecordsManager } from '@/composables/useFetchRecordsManager';
import { useFtpFileManager } from '@/composables/useFtpFileManager';


// Filters (empty for now)
const filters = ref({});
const isRefreshing = ref(false);

// Tabs (cards)
const cards = ref([
  { title: 'Recon', type: 'recon_ftp', class: '', count: 0 },
  { title: 'Recon Archive', type: 'recon_ftp_archives', class: '', count: 0 },
]);

// Composable logic for FTP
const {
  records,
  apiError,
  fetchRecords,
  fetchRecordCount,
  refreshData,
} = useFetchRecordsManager('ftp');

const {
   renameFile,
   deleteFile,
   downloadFile,
} = useFtpFileManager()



// Active tab
const activeCard = ref(cards.value[0].type);

// Menu open state to track which file's menu is open
const openMenu = ref<string | null>(null);

// Fetch data on mount
onMounted(async () => {
  for (const card of cards.value) {
    card.count = await fetchRecordCount(card);
  }
  await fetchRecords(cards.value[0]);
});

// Tab select handler
const onSelectCard = async (card: typeof cards.value[0]) => {
  activeCard.value = card.type;
  await fetchRecords(card);
  openMenu.value = null; // close menu when switching tabs
};

// Filtered records computed
const filteredRecords = computed(() => records.value);

// Menu toggle handler
const toggleMenu = (file: string) => {
  openMenu.value = openMenu.value === file ? null : file;
};

// Close menu handler (for outside clicks)
const closeMenu = () => {
  openMenu.value = null;
};

// Close menu on outside click
document.addEventListener('click', (e) => {
  if (!(e.target as HTMLElement).closest('.menu-wrapper')) {
    closeMenu();
  }
});

// Menu actions
const handleDownload = (file: string) => {
  console.log('Download', file);
  // TODO: call FTPManager.download(file)
  openMenu.value = null;
};

const handleRename = async (file: string) => {
  const newName = prompt('Enter new name for the file:', file);
  if (!newName || newName.trim() === '' || newName === file) return;

  const type = activeCard.value; 
  console.log(type);

  try {
    await renameFile(type, file, newName);
    await fetchRecords(cards.value.find(c => c.type === type)!);
    console.log(`Renamed "${file}" to "${newName}"`);
    refreshAllData();
  } catch (error) {
    console.error('Rename failed', error);
    alert('Rename failed. Please try again.');
  } finally {
    openMenu.value = null;
  }
};


const handleDelete = (file: string) => {
  console.log('Delete', file);
  // TODO: call FTPManager.delete(file)
  openMenu.value = null;
};
const refreshAllData = async () => {
  for (const card of cards.value) {
    await refreshData(card);
    card.count = await fetchRecordCount(card);
    await fetchRecords(card);
  }
};
</script>

<template>
  <div class="ftp-view">
    <div class="main-container">
      <!-- Sidebar -->
      <div class="sidebar">
        <SidebarTab
          v-for="card in cards"
          :key="card.type"
          :tab="card"
          :isActive="activeCard === card.type"
          :class="{ active: activeCard === card.type }"
          @click="onSelectCard(card)"
        />
      </div>

      <!-- File List -->
      <div class="file-list-container">
        <!-- Refresh button -->
          <div class="refresh-container">
            <button @click="refreshAllData" :disabled="isRefreshing">
              {{ isRefreshing ? 'Refreshing...' : 'Refresh' }}
            </button>
       </div>

        <div v-if="apiError" class="error-message">
          {{ apiError }}
        </div>

        <div v-else>
          <div
            v-for="file in filteredRecords"
            :key="file"
            class="file-item"
            style="display: flex; justify-content: space-between; align-items: center; position: relative;"
          >
            <span class="file-name" style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              {{ file }}
            </span>

            <!-- 3-dot Menu -->
            <div class="menu-wrapper" style="position: relative;">
              <button
                class="menu-trigger"
                @click.stop="toggleMenu(file)"
                aria-label="Options"
              >
                ⋮
              </button>

              <div v-if="openMenu === file" class="menu-dropdown">
                <button class="menu-button" @click="handleDownload(file, activeCard)">Download</button>
                <button class="menu-button" @click="handleRename(file, activeCard)">Rename</button>
                <button class="menu-button" @click="handleDelete(file, activeCard)">Delete</button>
              </div>
            </div>
          </div>

          <div v-if="filteredRecords.length === 0" class="no-results">
            No files found.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ftp-view {
  font-family: sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-container {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 180px;
  background-color: #fff8fc;
  border-right: 1px solid #ddd;
  padding: 10px;
}

.sidebar .active {
  background-color: #e6e6ff;
  font-weight: bold;
}

.file-list-container {
  flex: 1;
  background: #fdf7ff;
  padding: 10px;
  overflow-y: auto;
}
</style>
