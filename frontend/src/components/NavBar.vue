<template>
  <v-app-bar flat border color="surface" class="px-2">
    <v-app-bar-title class="d-flex align-center" style="min-width: 0">
      <v-icon color="primary" class="mr-2">mdi-shield-lock</v-icon>
      <span class="text-primary font-weight-bold text-no-wrap">FitGate</span>
      <span class="text-medium-emphasis ml-2 text-body-2 text-no-wrap">
        · Reconocimiento facial
      </span>
    </v-app-bar-title>

    <template #append>
      <div class="d-flex align-center" style="gap: 4px">
        <v-btn
          :to="{ name: 'socios' }"
          variant="text"
          size="small"
          prepend-icon="mdi-account-group"
          :active="route.name === 'socios'"
        >
          Socios
        </v-btn>
        <v-btn
          :to="{ name: 'enrolamiento' }"
          variant="text"
          size="small"
          prepend-icon="mdi-face-recognition"
          :active="route.name === 'enrolamiento'"
        >
          Enrolar
        </v-btn>

        <v-divider vertical class="mx-2 my-3" />

        <v-btn
          :to="{ name: 'reconocimiento' }"
          color="primary"
          variant="flat"
          size="small"
          prepend-icon="mdi-camera-account"
          class="mx-1"
        >
          Reconocer
        </v-btn>
      </div>
    </template>
  </v-app-bar>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>
