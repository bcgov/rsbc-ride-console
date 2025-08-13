<script setup lang="ts">
defineProps({
  event: {
    type: Object ,
    required: true
  }
});
defineEmits(['select']);
</script>

<template>
  <div class="event-list-item" @click="$emit('select', event)">
    <div class="item-title">
      <strong>{{ event.errorReason || '<Error Reason Unknown>' }}</strong>
    </div>
    <div class="item-subtext">{{ event.eventType }}</div>
    <div class="item-subtext">{{ event.datasource }}</div>
    <div class="arrow">›</div>
  </div>
</template>



<style scoped>
.event-list-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  position: relative;
}
.event-list-item:hover {
  background-color: #f0f0f0;
}
.item-title {
  font-size: 1rem;
  margin-bottom: 4px;
}
.item-subtext {
  font-size: 0.85rem;
  color: #777;
}
.arrow {
  position: absolute;
  right: 10px;
  top: 18px;
  color: #aaa;
  font-weight: bold;
}
</style>
