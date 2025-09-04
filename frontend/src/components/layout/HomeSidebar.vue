
<script setup lang="ts">
defineProps<{
  tabs: Array<{ name: string; label: string; icon: string }>;
  activeTab: string;
}>();

defineEmits(['tab-click']);
</script>
<template>
  <div class="sidebar">
    <div
      v-for="tab in tabs"
      :key="tab.name"
      :class="['sidebar-tab', { active: activeTab === tab.name }]"
      @click="$emit('tab-click', tab.name)"
    >
      <div
       class="icon-wrapper"
        :class="{ selected: activeTab === tab.name }"
        >
        <span class="material-icons">{{ tab.icon }}</span>
      </div>
      <span class="label">{{ tab.label }}</span>
    </div>
  </div>
</template>


<style scoped>
.sidebar {
  width: 80px;
  background-color: #fef7ff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  border-right: 1px solid #e0e0e0;
}

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
  background-color: #ede7f6;
}

.material-icons {
  font-size: 24px;
}
</style>
