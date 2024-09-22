<template>
    <div class="login-container">
      <div class="login-form-container">
        <div class="app-title">WFH Scheduler</div>
        <div class="login-form">
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="email">Email</label>
              <input type="email" id="email" v-model="email" required>
            </div>
            <div class="form-group">
              <label for="password">Password</label>
              <input type="password" id="password" v-model="password" required>
            </div>
            <button type="submit">Log In</button>
          </form>
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>

  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import axios from 'axios';
  
  const router = useRouter();
  const email = ref('');
  const password = ref('');
  const errorMessage = ref('');
  
  const handleLogin = async () => {
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/login`, {
        email: email.value,
        password: password.value
      });
  
      if (response.data.staff_id) {
        // Store the user info in localStorage
        localStorage.setItem('user', JSON.stringify({
          staff_id: response.data.staff_id,
          name: response.data.name,
          role: response.data.role
        }));
  
        // Redirect to dashboard
        router.push('/dashboard');
      }
    } catch (error) {
      if (error.response) {
        errorMessage.value = error.response.data.message;
      } else {
        errorMessage.value = 'An error occurred. Please try again.';
      }
    }
  };
  </script>
  
  <style scoped>
  .login-container {
    height: 100vh;
    width: 100vw;
    display: flex;
    justify-content: center;
    align-items: center;
    background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('@/assets/images/login-image.jpg');
    background-size: cover;
    background-position: center;
  }
  
  .login-form-container {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 15px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }
  
  .app-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #3498db;
    margin-bottom: 1.5rem;
    text-align: center;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  .login-form h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #2c3e50;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #34495e;
    font-weight: 600;
    text-align: left;
  }
  
  input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
  }
  
  input:focus {
    outline: none;
    border-color: #3498db;
  }
  
  button {
    width: 100%;
    padding: 0.75rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: background-color 0.3s ease;
  }
  
  button:hover {
    background-color: #2980b9;
  }
  
  .error-message {
    color: #e74c3c;
    text-align: center;
    margin-top: 1rem;
  }
  </style>