<template>
  <v-app>
    <NavBar />
    <v-main class="app-background">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
</script>

<style>
.app-background {
  background: #f5f6f8;
}
</style>
