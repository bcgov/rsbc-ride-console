<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import SidebarTab from '@/components/layout/SidebarTab.vue';
import { useFetchRecordsManager } from '@/composables/useFetchRecordsManager';
import { useFtpFileManager } from '@/composables/useFtpFileManager';
import FetchRecordsService from '@/services/fetchRecordsService';
import { StorageKey } from '@/utils/constants';
import Spinner from '@/components/layout/Spinner.vue';

const service = FetchRecordsService;
const storageType = window.sessionStorage;

const filters = ref({});
const isRefreshing = ref(false);

const cards = ref([
  { title: 'Recon', type: 'recon_ftp', class: '', count: 0 },
  { title: 'Recon Archive', type: 'recon_ftp_archives', class: '', count: 0 },
]);

const activeCard = ref(cards.value[0]);

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
} = useFtpFileManager();

const openMenu = ref<string | null>(null);

onMounted(async () => {
  isLoading.value = true;
  cancelLoading.value = false;

  try {
    // Fetch counts for all cards
    for (const card of cards.value) {
      if (cancelLoading.value) break;
      card.count = await fetchRecordCount(card);
    }

    // Fetch files for active tab
    if (!cancelLoading.value) {
      await fetchRecords(activeCard.value);
    }
  } catch (error) {
    console.error('FTP loading error', error);
  } finally {
    isLoading.value = false;
  }
});



const onSelectCard = async (card: typeof cards.value[0]) => {
  activeCard.value = card;
  openMenu.value = null;

  // Start spinner
  isLoading.value = true;
  currentFileProcessing.value = 'Loading files...';
  cancelLoading.value = false;

  try {
    // Clear cached data
    storageType.removeItem(`${StorageKey.EVENTS}_ftp_${card.type}`);

    // Fetch fresh records
    const response = await service.fetchRecords('ftp', card.type);
    const data = response.data || [];

    // Update reactive array to trigger UI update
    records.value = data;

    // Optional: cache data
    storageType.setItem(`${StorageKey.EVENTS}_ftp_${card.type}`, JSON.stringify(data));
  } catch (error) {
    console.error('Failed to load files:', error);
    alert('Failed to load files.');
  } finally {
    // Stop spinner
    isLoading.value = false;
    currentFileProcessing.value = null;
  }
};


const filteredRecords = computed(() => records.value);

const toggleMenu = (file: string) => {
  openMenu.value = openMenu.value === file ? null : file;
};

const closeMenu = () => {
  openMenu.value = null;
};

document.addEventListener('click', (e) => {
  if (!(e.target as HTMLElement).closest('.menu-wrapper')) {
    closeMenu();
  }
});

const currentFileProcessing = ref<string | null>(null);

// Stop any ongoing operation
const stopLoading = () => {
  cancelLoading.value = true;
  isLoading.value = false;
  currentFileProcessing.value = null;
};


const handleDownload = async (file: string) => {
  isLoading.value = true;
  currentFileProcessing.value = `Downloading ${file}...`;
  cancelLoading.value = false;

  try {
    const blob = await downloadFile(activeCard.value.type as 'recon_ftp' | 'recon_ftp_archives', file);
    if (cancelLoading.value) return;

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file;
    a.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    if (!cancelLoading.value) console.error('Download failed', error);
    alert(`Download failed for ${file}`);
  } finally {
    isLoading.value = false;
    currentFileProcessing.value = null;
    openMenu.value = null;
    cancelLoading.value = false;
  }
};

const handleRename = async (file: string) => {
  const newName = prompt('Enter new name for the file:', file);
  if (!newName || newName.trim() === '' || newName === file) return;

  isLoading.value = true;
  currentFileProcessing.value = `Renaming ${file}...`;
  cancelLoading.value = false;

  try {
    await renameFile(activeCard.value.type as 'recon_ftp' | 'recon_ftp_archives', file, newName);
    if (cancelLoading.value) return;

    await fetchRecords(activeCard.value);
    refreshAllData();
  } catch (error) {
    if (!cancelLoading.value) console.error('Rename failed', error);
    alert(`Rename failed for ${file}`);
  } finally {
    isLoading.value = false;
    currentFileProcessing.value = null;
    openMenu.value = null;
    cancelLoading.value = false;
  }
};

const handleDelete = async (file: string) => {
  const confirmDelete = window.confirm(`Are you sure you want to delete "${file}"?`);
  if (!confirmDelete) return;

  isLoading.value = true;
  currentFileProcessing.value = `Deleting ${file}...`;
  cancelLoading.value = false;

  try {
    await deleteFile(activeCard.value.type as 'recon_ftp' | 'recon_ftp_archives', file);
    if (cancelLoading.value) return;

    await fetchRecords(activeCard.value);
    refreshAllData();
  } catch (error) {
    if (!cancelLoading.value) console.error('Delete failed', error);
    alert(`Delete failed for ${file}`);
  } finally {
    isLoading.value = false;
    currentFileProcessing.value = null;
    openMenu.value = null;
    cancelLoading.value = false;
  }
};





const refreshAllData = async () => {
  isLoading.value = true; // start spinner
  try {
    // Refresh counts for all tabs
    for (const card of cards.value) {
      storageType.removeItem(`${StorageKey.EVENT_COUNT}_ftp_${card.type}`);
      card.count = await fetchRecordCount(card);
      if (!isLoading.value) return; // early exit if stopped
    }

    // Refresh and cache data for all tabs
    for (const card of cards.value) {
      const response = await service.fetchRecords('ftp', card.type);
      if (!isLoading.value) return; // early exit if stopped
      const data = response.data || [];
      storageType.setItem(`${StorageKey.EVENTS}_${'ftp'}_${card.type}`, JSON.stringify(data));
    }

    // Load active tab's data
    await fetchRecords(activeCard.value);
  } catch (error) {
    console.error('Refresh failed:', error);
  } finally {
    isLoading.value = false; // stop spinner
  }
};


const isLoading = ref(false);
const cancelLoading = ref(false);





</script>

<template>

  <div class="ftp-view">
      <div v-if="isLoading" class="loading-overlay">
        <div class="spinner-container">
          <Spinner />
          <h2>{{ currentFileProcessing || 'Loading...' }}</h2>
          <button class="stop-button" @click="stopLoading" aria-label="Stop loading">
            × Stop
          </button>
        </div>
      </div>




    <div class="main-container">
      <!-- Sidebar -->
      <div class="sidebar">
        <SidebarTab
          v-for="card in cards"
          :key="card.title"
          :tab="card"
          :isActive="activeCard === card"
          :class="{ active: activeCard === card }"
          @click="onSelectCard(card)"
        />
      </div>

      <!-- File List -->
      <div class="file-list-container">
        <!-- Refresh -->
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



              <!-- 3-dot menu -->
              <div class="menu-wrapper" style="position: relative;">
                <span
                  class="material-icons menu-trigger"
                  @click.stop="toggleMenu(file)"
                  aria-label="Options"
                  style="cursor: pointer; user-select: none;"
                >
                  more_vert
                </span>

                <div v-if="openMenu === String(file)" class="menu-dropdown">
                  <button class="menu-button" @click="handleDownload(file)">Download</button>
                  <button class="menu-button" @click="handleRename(file)">Rename</button>
                  <button class="menu-button" @click="handleDelete(file)">Delete</button>
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

.refresh-container {
  margin-bottom: 10px;
}

.menu-dropdown {
  position: absolute;
  top: 30px;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  z-index: 100;
  box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}

.menu-button {
  display: block;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
}

.menu-button:hover {
  background-color: #f0f0f0;
}
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  pointer-events: all;
  flex-direction: column;
}



.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px; /* space between spinner, text, and button */
}

.stop-button {
  display: flex;
  align-items: center;
  gap: 8px; /* space between icon and text */
  padding: 8px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.stop-button:hover {
  background-color: #c0392b;
}

.stop-button .material-icons {
  font-size: 1.2rem;
}


</style>
