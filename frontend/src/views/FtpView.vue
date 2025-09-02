<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import SidebarTab from '@/components/layout/SidebarTab.vue';
import { useFetchRecordsManager } from '@/composables/useFetchRecordsManager';
import { useFtpFileManager } from '@/composables/useFtpFileManager';
import FetchRecordsService from '@/services/fetchRecordsService';
import { StorageKey } from '@/utils/constants';

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
  for (const card of cards.value) {
    card.count = await fetchRecordCount(card);
  }
  await fetchRecords(activeCard.value);
});

const onSelectCard = async (card: typeof cards.value[0]) => {
  activeCard.value = card;
  await fetchRecords(card);
  openMenu.value = null;
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

const handleDownload = async (file: string) => {
  try {
    const blob = await downloadFile(activeCard.value.type  as 'recon_ftp' | 'recon_ftp_archives', file);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file;
    a.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
    alert('Failed to download file.');
  } finally {
    openMenu.value = null;
  }
};

const handleRename = async (file: string) => {
  const newName = prompt('Enter new name for the file:', file);
  if (!newName || newName.trim() === '' || newName === file) return;

  try {
    await renameFile(activeCard.value.type  as 'recon_ftp' | 'recon_ftp_archives', file, newName);
    await fetchRecords(activeCard.value);
    refreshAllData();
  } catch (error) {
    console.error('Rename failed', error);
    alert('Rename failed. Please try again.');
  } finally {
    openMenu.value = null;
  }
};

const handleDelete = async (file: string) => {
  const confirmDelete = window.confirm(`Are you sure you want to delete "${file}"?`);
  if (!confirmDelete) return;

  try {
    await deleteFile(activeCard.value.type as 'recon_ftp' | 'recon_ftp_archives', file);

    await fetchRecords(activeCard.value);
    refreshAllData();
  } catch (error) {
    console.error('Delete failed', error);
    alert('Delete failed. Please try again.');
  } finally {
    openMenu.value = null;
  }
};


const refreshAllData = async () => {
  // Refresh counts for all tabs
  for (const card of cards.value) {
    storageType.removeItem(`${StorageKey.EVENT_COUNT}_error_${card.type}`);
    card.count = await fetchRecordCount(card);
  }

  // Refresh and cache data for all tabs (including inactive)
  for (const card of cards.value) {
    const response = await service.fetchRecords('ftp', card.type);
    const data = response.data || [];
    storageType.setItem(`${StorageKey.EVENTS}_${'ftp'}_${card.type}`, JSON.stringify(data));
  }

  // Finally, load active tab's data into UI
  await fetchRecords(activeCard.value);
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
</style>
