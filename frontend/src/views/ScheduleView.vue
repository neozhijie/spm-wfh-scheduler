<template>
  <Navbar />
    <div class="dashboard">

      <h1>Welcome to your Schedule Dashboard</h1>
      <p>You are logged in as {{ user.staff_fname }} {{ user.staff_lname }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import Navbar from '@/components/Navbar.vue';
  const user = ref({});
  
  onMounted(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      user.value = JSON.parse(storedUser);
    }
  });
  </script>
  
  <style scoped>
  .dashboard {
    padding: 2rem;
  }
  </style>