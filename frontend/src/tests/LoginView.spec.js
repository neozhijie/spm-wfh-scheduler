// src/tests/LoginView.spec.js
import { mount } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import axios from 'axios';
import { vi, describe, it, beforeEach, afterEach, expect } from 'vitest';

vi.mock('axios');

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/schedule',
      name: 'Schedule',
      component: { template: '<div>Schedule</div>' }
    }
  ]
});

describe('LoginView.vue', () => {
  let wrapper;
  const mockUserData = {
    staff_id: 1,
    staff_fname: 'John',
    staff_lname: 'Doe',
    email: 'john.doe@example.com'
  };

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset router
    router.push('/');
    
    // Create fresh wrapper
    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        stubs: ['router-link']
      }
    });
  });

  afterEach(() => {
    wrapper.unmount();
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders the login form with all required elements', () => {
    expect(wrapper.find('.app-title').text()).toBe('WFH Scheduler');
    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true);
    expect(wrapper.find('form').exists()).toBe(true);
  });

  it('validates required fields before submission', async () => {
    const form = wrapper.find('form');
    await form.trigger('submit.prevent');
    
    // Check if HTML5 validation is working
    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    
    expect(emailInput.element.validity.valid).toBe(false);
    expect(passwordInput.element.validity.valid).toBe(false);
  });

  it('successfully logs in and redirects with correct credentials', async () => {
    axios.post.mockResolvedValueOnce({ data: mockUserData });

    await wrapper.find('input#email').setValue('john.doe@example.com');
    await wrapper.find('input#password').setValue('correctpassword');
    await wrapper.find('form').trigger('submit.prevent');

    expect(axios.post).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_URL}/api/login`,
      {
        email: 'john.doe@example.com',
        password: 'correctpassword'
      }
    );

    // Verify localStorage
    expect(JSON.parse(localStorage.getItem('user'))).toEqual(mockUserData);

    // Verify router navigation
    await router.isReady();
    expect(router.currentRoute.value.path).toBe('/schedule');
  });

  it('handles network errors appropriately', async () => {
    axios.post.mockRejectedValueOnce(new Error('Network Error'));

    await wrapper.find('input#email').setValue('john.doe@example.com');
    await wrapper.find('input#password').setValue('password');
    await wrapper.find('form').trigger('submit.prevent');

    await wrapper.vm.$nextTick();
    expect(wrapper.find('.error-message').text()).toBe('An error occurred. Please try again.');
  });

  it('handles invalid credentials error', async () => {
    const errorMessage = 'Invalid email or password';
    axios.post.mockRejectedValueOnce({
      response: { data: { message: errorMessage } }
    });

    await wrapper.find('input#email').setValue('john.doe@example.com');
    await wrapper.find('input#password').setValue('wrongpassword');
    await wrapper.find('form').trigger('submit.prevent');

    await wrapper.vm.$nextTick();
    expect(wrapper.find('.error-message').text()).toBe(errorMessage);
  });


});
