<template>
  <nav class="navbar navbar-expand-lg custom-navbar">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">WFH Scheduler</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNavDropdown">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

        </ul>
        <ul class="navbar-nav">
          <li class="nav-item">
            <router-link class="nav-link" to="/schedule">My Schedule</router-link>
          </li>
          <li class="nav-item" v-if="user.role==3">
            <router-link class="nav-link" to="/teamschedule-manager">Team Schedule</router-link>
          </li>
          <li class="nav-item" v-if="user.role==2">
            <router-link class="nav-link" to="/teamschedule-staff">Team Schedule</router-link>
          </li>
          <li class="nav-item"  v-if="user.role==2 ||user.role==3 ||user.dept=='HR'">
            <router-link class="nav-link" to="/application">Apply</router-link>
          </li>
          <li class="nav-item" v-if="user.position=='Director' || user.role==3 || user.position=='MD'">
            <router-link class="nav-link" to="/requests">Requests</router-link>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              {{ user.fname }}
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdownMenuLink">
              <li><a class="dropdown-item" href="#" @click="logout">Logout</a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const user = ref({});

const updateUserFromStorage = () => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
  } else {
    user.value = {};
  }
};

onMounted(() => {
  updateUserFromStorage();

  // Listen for storage events (in case user logs in in another tab)
  window.addEventListener('storage', (event) => {
    if (event.key === 'user') {
      updateUserFromStorage();
    }
  });
});

// Watch for route changes
watch(() => router.currentRoute.value, () => {
  updateUserFromStorage();
}, { immediate: true });

const logout = () => {
  localStorage.removeItem('user');
  user.value = {};
  router.push('/');
};
</script>

<style scoped>
.navbar .container-fluid {
  padding-right: 0;
}

.custom-navbar {
  background-color: #141b4d;
}

.navbar-brand,
.nav-link {
  color: white !important;
}

.nav-item {
  padding: 1rem;
}

.nav-link:hover{
  color: #C69200!important;
}
.nav-link.router-link-active {
  color: #C69200 !important;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(255, 255, 255, 0.55)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

.navbar-toggler {
  border-color: rgba(255, 255, 255, 0.1);
}

.dropdown-menu {
  background-color: #141b4d;
  border-right: 0;
}

.dropdown-item {
  color: white;
}

.dropdown-item:hover {
  background-color: #1e2a6d;
  color: #C69200;
}
</style>