<template>
    <div class="login-container">
      <div class="login-form-container">
        <div class="logo-container">
        <img :src="companyLogo" alt="Company Logo" class="company-logo">
      </div>
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
  import companyLogo from '@/assets/images/company-logo.jpg';
  
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
        
        localStorage.setItem('user', JSON.stringify(response.data));
  
        // Redirect to dashboard
        router.push('/schedule');
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
    text-align: center;
    margin-bottom: 1rem;
  }

  .company-logo {
  height: 60px;
  width: auto;
  max-width: 200px;
  object-fit: contain;
  }
  
  .login-form-container {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 2.5rem 2rem;
    border-radius: 15px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.6s ease-out;
  }
  
  .app-title {
    font-size: 2.5rem;
    font-weight: bold;
    color: #141b4d;
    margin-bottom: 1.5rem;
    text-align: center;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  .login-form h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #141b4d;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
    opacity: 0;
    animation: fadeIn 0.6s ease-out forwards;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #141b4d;
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
    transition: all 0.3s ease;
  }
  
  input:focus {
    outline: none;
    border-color: #141b4d;
  }
  
  button {
    width: 100%;
    padding: 0.75rem;
    background-color: #141b4d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: background-color 0.3s ease;
    opacity: 0;
    animation: fadeIn 0.6s ease-out forwards;
    animation-delay: 0.6s;
    transition: all 0.3s ease;
  }
  
  button:hover {
    background-color: #111d6c;
  }
  
  .error-message {
    color: #e74c3c;
    text-align: center;
    margin-top: 1rem;
    transition: all 0.3s ease;
  }

  @media (max-width: 576px) {
  .company-logo {
    height: 45px;
  }
  
  .app-title {
    font-size: 2rem;
  }
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.form-group:nth-child(1) {
  animation-delay: 0.2s;
}

.form-group:nth-child(2) {
  animation-delay: 0.4s;
}


  </style>