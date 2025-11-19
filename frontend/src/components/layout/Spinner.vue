<script setup lang="ts">
import { ProgressSpinner } from '@/lib/primevue';
</script>

<template>
  <ProgressSpinner
    style="width: 50px; height: 50px"
    stroke-width="4"
  />
</template>

<style lang="scss" scoped>
:deep(.p-progress-spinner-circle) {
  stroke: #00004d !important;
}




.stop-btn {
  margin-top: 20px;
  padding: 6px 12px;
  border: none;
  background-color: #00004d;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.stop-btn:hover {
  background-color: #3333ff;
}

</style>


