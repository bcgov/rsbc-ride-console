<script setup lang="ts">
defineProps<{
  tab: {
    title: string;
    type: string;
    class: string;
    count: number;
  };
  isActive?: boolean;
}>();

defineEmits(['click']);
</script>

<template>
  <div
    class="sidebar-tab"
    :class="[tab.class, { active: isActive }]"
    @click="$emit('click', tab)"
  >
    <div class="title">{{ tab.title }}</div>
    <div class="count">{{ tab.count > 99 ? '99+' : tab.count }}</div>
  </div>
</template>

<style scoped>
.sidebar-tab {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 10px;
  background-color: #f2f2f2;
  color: #333;
  transition: background-color 0.3s, border-left 0.3s;
  border-left: 4px solid transparent;
}

.sidebar-tab:hover {
  opacity: 0.9;
}

/* Active tab highlight */
.sidebar-tab.active {
  background-color: #e9e4fc;
  border-left: 4px solid #673ab7;
  font-weight: 600;
}

/* Tab-specific colors */
.sidebar-tab.red {
  background-color: #ffe5e5;
  color: #8b0000;
}
.sidebar-tab.darkred {
  background-color: #f8d7da;
  color: #5a0000;
}
.sidebar-tab.orange {
  background-color: #fff3e0;
  color: #cc7000;
}
.sidebar-tab.green {
  background-color: #e0f7ea;
  color: #009688;
}
.sidebar-tab.blue {
  background-color: #e3f2fd;
  color: #1976d2;
}
.sidebar-tab.purple {
  background-color: #ede7f6;
  color: #6a1b9a;
}
.sidebar-tab.grey {
  background-color: #f0f0f0;
  color: #555;
}
</style>
