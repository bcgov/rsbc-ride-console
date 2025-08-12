
<template>
  <div
    class="sidebar-tab"
    :class="tab.class"
    @click="$emit('click', tab)"
  >
    <div class="title">{{ tab.title }}</div>
    <div class="count">{{ tab.count > 99 ? '99+' : tab.count }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  tab: Object
});

defineEmits(['click']);
</script>

<style scoped>



.sidebar-tab {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 10px;
  background-color: #f2f2f2;
  color: #333;
}

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

.sidebar-tab:hover {
  opacity: 0.9;
}
</style>
