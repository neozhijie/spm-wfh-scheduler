<template>
    <div class="dashboard">
      <h1>Welcome to your Dashboard</h1>
      <p>You are logged in as {{ user.fname }} {{ user.lname }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  
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