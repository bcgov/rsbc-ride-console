<script setup lang="ts">
import { Message } from '@/lib/primevue';
import { storeToRefs } from 'pinia';
import { useRoute, useRouter } from 'vue-router';

import { useConfigStore } from '@/store';

// Store
const { getConfig } = storeToRefs(useConfigStore());

const route = useRoute();
const router = useRouter();
const redirectParam = route.query.redirect as string | undefined;
if (redirectParam) {
  let queryParameters = Object.entries(route.query)
    .filter(([key]) => key !== 'redirect')
    .reduce(
      (acc, [key, value]) => {
        acc[key] = value as string;
        return acc;
      },
      {} as Record<string, string>
    );
  router.replace({ path: redirectParam, query: queryParameters });
}

// Actions
const frontEcosystem: Array<{ text: string; href: string }> = [
  {
    text: 'Vue 3',
    href: 'https://vuejs.org/'
  },
  {
    text: 'Pinia',
    href: 'https://pinia.vuejs.org/'
  },
  {
    text: 'PrimeVue',
    href: 'https://primevue.org/'
  },
  {
    text: 'Vitest',
    href: 'https://vitest.dev/'
  }
];

const backEcosystem: Array<{ text: string; href: string }> = [
  {
    text: 'Express',
    href: 'https://expressjs.com/'
  },
  {
    text: 'Jest',
    href: 'https://jestjs.io/'
  }
];

const languagesEcosystem: Array<{ text: string; href: string }> = [
  {
    text: 'TypeScript',
    href: 'https://www.typescriptlang.org/'
  }
];
</script>

<template>
  <div>
    <Message
      v-if="getConfig?.notificationBanner"
      severity="warn"
    >
      {{ getConfig?.notificationBanner }}
    </Message>

    <div class="text-center">
      <h1 class="font-bold">Welcome to the RIDE Console!</h1>
      <h2>Frontend Ecosystem</h2>
      <a
        v-for="(eco, i) in frontEcosystem"
        :key="i"
        :href="eco.href"
        class="mx-3"
        target="_blank"
      >
        {{ eco.text }}
      </a>
      <h2>Backend Ecosystem</h2>
      <a
        v-for="(eco, i) in backEcosystem"
        :key="i"
        :href="eco.href"
        class="mx-3"
        target="_blank"
      >
        {{ eco.text }}
      </a>
      <h2>Languages</h2>
      <a
        v-for="(eco, i) in languagesEcosystem"
        :key="i"
        :href="eco.href"
        class="mx-3"
        target="_blank"
      >
        {{ eco.text }}
      </a>
    </div>
  </div>
</template>
