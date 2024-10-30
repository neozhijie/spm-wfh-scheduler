// src/tests/ApplicationView.spec.js
import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import ApplicationView from '../views/ApplicationView.vue';
import axios from 'axios';
import Navbar from '@/components/Navbar.vue';

vi.mock('axios');

describe('ApplicationView.vue', () => {
  let wrapper;
  const mockUser = {
    staff_id: 1,
    reporting_manager: 2,
    dept: 'IT',
    position: 'Developer'
  };

  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(() => JSON.stringify(mockUser)),
      setItem: vi.fn(),
      clear: vi.fn()
    };
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock
    });

    // Mount component
    wrapper = mount(ApplicationView, {
      global: {
        components: {
          Navbar
        },
        stubs: ['Navbar']
      }
    });
  });

  afterEach(() => {
    wrapper.unmount();
    vi.clearAllMocks();
  });

  it('renders the form with all required fields', () => {
    expect(wrapper.find('h2').text()).toBe('Work From Home Request Form');
    expect(wrapper.find('#startDate').exists()).toBe(true);
    expect(wrapper.find('#reason').exists()).toBe(true);
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3);
    expect(wrapper.find('#recurring').exists()).toBe(true);
  });

  it('validates start date is not on weekend', async () => {
    // Set a Saturday date
    const saturdayDate = '2024-11-02'; // Modify this to a future Saturday
    await wrapper.find('#startDate').setValue(saturdayDate);
    await wrapper.find('#startDate').trigger('change');

    expect(wrapper.vm.startDateError).toBe('Start date cannot be a weekend.');
  });

  it('handles recurring request toggle correctly', async () => {
    // Set valid start date first
    const validDate = new Date();
    validDate.setDate(validDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(validDate.toISOString().split('T')[0]);
    
    // Toggle recurring checkbox
    await wrapper.find('#recurring').setValue(true);
    
    expect(wrapper.find('#endDate').exists()).toBe(true);
  });

  it('validates end date for recurring requests', async () => {
    // Set valid start date
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    
    // Enable recurring
    await wrapper.find('#recurring').setValue(true);
    
    // Set invalid end date (before start date)
    await wrapper.find('#endDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#endDate').trigger('change');

    expect(wrapper.vm.endDateError).toBe('End date must be after the start date.');
  });

  it('successfully submits the form with valid data', async () => {
    const mockResponse = { data: { message: 'Success' } };
    axios.post.mockResolvedValueOnce(mockResponse);

    // Fill form with valid data
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Working from home');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');

    // Verify API call
    expect(axios.post).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_URL}/api/request`,
      expect.objectContaining({
        staff_id: mockUser.staff_id,
        manager_id: mockUser.reporting_manager,
        reason_for_applying: 'Working from home',
        duration: 'FULL_DAY'
      })
    );
  });

  it('handles API errors during submission', async () => {
    const errorMessage = 'Server error';
    axios.post.mockRejectedValueOnce({
      response: { data: { message: errorMessage } }
    });

    // Mock window.alert
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    // Fill and submit form
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Working from home');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
    await wrapper.find('form').trigger('submit.prevent');

    expect(alertMock).toHaveBeenCalledWith(`Error: ${errorMessage}`);
  });

  it('resets form after successful submission', async () => {
    axios.post.mockResolvedValueOnce({ data: { message: 'Success' } });

    // Fill form
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Working from home');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
    
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');

    // Verify form reset
    expect(wrapper.vm.startDate).toBe('');
    expect(wrapper.vm.reason).toBe('');
    expect(wrapper.vm.dayType).toBe('');
  });

  it('disables submit button when form is invalid', async () => {
    const submitButton = wrapper.find('button[type="submit"]');
    expect(submitButton.attributes('disabled')).toBeDefined();

    // Fill form partially
    await wrapper.find('#startDate').setValue('2024-11-01');
    expect(submitButton.attributes('disabled')).toBeDefined();

    // Fill form completely
    await wrapper.find('#reason').setValue('Working from home');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
    await wrapper.vm.$nextTick();

    expect(submitButton.attributes('disabled')).toBeUndefined();
  });

  it('validates day type selection', async () => {
    const dayTypes = ['FULL_DAY', 'HALF_DAY_AM', 'HALF_DAY_PM'];
    
    for (const type of dayTypes) {
      // Reset form state
      wrapper.vm.resetForm();
      
      // Fill required fields
      const startDate = new Date();
      startDate.setDate(startDate.getDate() + 1);
      await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
      await wrapper.find('#reason').setValue('Test WFH request');
      
      // Select day type
      await wrapper.find(`input[value="${type}"]`).setValue(true);
      
      // Verify day type is set correctly
      expect(wrapper.vm.dayType).toBe(type);
      
      // Verify form becomes valid
      expect(wrapper.vm.isFormValid).toBe(true);
      
      // Mock API response
      axios.post.mockResolvedValueOnce({ data: { message: 'Success' } });
      
      // Submit form
      await wrapper.find('form').trigger('submit.prevent');
      
      // Verify API call includes correct day type
      expect(axios.post).toHaveBeenCalledWith(
        `${import.meta.env.VITE_API_URL}/api/request`,
        expect.objectContaining({
          duration: type,
          reason_for_applying: 'Test WFH request',
          date: startDate.toISOString().split('T')[0]
        })
      );
    }
  });
  
  it('handles form submission with recurring request', async () => {
    // Set valid dates for recurring request
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 5);
  
    // Fill form with recurring request data
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#recurring').setValue(true);
    await wrapper.find('#endDate').setValue(endDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Recurring WFH request');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
  
    // Verify recurring fields are visible and properly set
    expect(wrapper.find('#endDate').exists()).toBe(true);
    expect(wrapper.vm.isRecurring).toBe(true);
  
    // Mock successful API response
    axios.post.mockResolvedValueOnce({ data: { message: 'Success' } });
  
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
  
    // Verify API call
    expect(axios.post).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_URL}/api/request`,
      expect.objectContaining({
        staff_id: mockUser.staff_id,
        manager_id: mockUser.reporting_manager,
        reason_for_applying: 'Recurring WFH request',
        date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        duration: 'FULL_DAY',
        dept: mockUser.dept,
        position: mockUser.position
      })
    );
  });
  
  it('validates date selections for recurring requests', async () => {
    // Set initial valid start date
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    
    // Enable recurring requests
    await wrapper.find('#recurring').setValue(true);
    
    // Test invalid end date (before start date)
    const invalidEndDate = new Date(startDate);
    invalidEndDate.setDate(startDate.getDate() - 1);
    await wrapper.find('#endDate').setValue(invalidEndDate.toISOString().split('T')[0]);
    await wrapper.find('#endDate').trigger('change');
    
    expect(wrapper.vm.endDateError).toBe('End date must be after the start date.');
    
    // Test valid end date
    const validEndDate = new Date(startDate);
    validEndDate.setDate(startDate.getDate() + 5);
    await wrapper.find('#endDate').setValue(validEndDate.toISOString().split('T')[0]);
    await wrapper.find('#endDate').trigger('change');
    
    expect(wrapper.vm.endDateError).toBe('');
  });
  
  it('handles form reset after successful submission', async () => {
    // Fill form with complete data
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#recurring').setValue(true);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 5);
    await wrapper.find('#endDate').setValue(endDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Test WFH request');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
  
    // Mock successful API response
    axios.post.mockResolvedValueOnce({ data: { message: 'Success' } });
  
    // Mock window.alert
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});
  
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
  
    // Verify form reset
    expect(wrapper.vm.startDate).toBe('');
    expect(wrapper.vm.endDate).toBe('');
    expect(wrapper.vm.isRecurring).toBe(false);
    expect(wrapper.vm.reason).toBe('');
    expect(wrapper.vm.dayType).toBe('');
    expect(wrapper.vm.startDateError).toBe('');
    expect(wrapper.vm.endDateError).toBe('');
    expect(wrapper.vm.showRecurringWarning).toBe(false);
  
    // Verify success message
    expect(alertMock).toHaveBeenCalledWith('WFH request submitted successfully.');
  });
  
  it('handles API errors during submission', async () => {
    // Fill form with valid data
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Test WFH request');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
  
    // Mock API error
    const errorMessage = 'Server error: Request could not be processed';
    axios.post.mockRejectedValueOnce({
      response: { data: { message: errorMessage } }
    });
  
    // Mock window.alert
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});
  
    // Submit form
    await wrapper.find('form').trigger('submit.prevent');
  
    // Verify error handling
    expect(alertMock).toHaveBeenCalledWith(`Error: ${errorMessage}`);
    
    // Verify form data is preserved
    expect(wrapper.vm.startDate).toBe(startDate.toISOString().split('T')[0]);
    expect(wrapper.vm.reason).toBe('Test WFH request');
    expect(wrapper.vm.dayType).toBe('FULL_DAY');
  });
  
  it('validates form submission button state', async () => {
    const submitButton = wrapper.find('button[type="submit"]');
    
    // Initially disabled
    expect(submitButton.attributes('disabled')).toBeDefined();

    // Fill form partially
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    
    // Button should still be disabled
    expect(submitButton.attributes('disabled')).toBeDefined();

    // Fill reason but leave day type empty
    await wrapper.find('#reason').setValue('Test WFH request');
    expect(submitButton.attributes('disabled')).toBeDefined();

    // Fill day type - now form should be valid
    await wrapper.find('#fullDay').setValue('FULL_DAY');
    await wrapper.vm.$nextTick();
    
    // Button should now be enabled
    expect(submitButton.attributes('disabled')).toBeUndefined();

    // Test button state with invalid date
    const weekendDate = new Date('2024-11-02'); // A Saturday
    await wrapper.find('#startDate').setValue(weekendDate.toISOString().split('T')[0]);
    await wrapper.find('#startDate').trigger('change');
    await wrapper.vm.$nextTick();

    // Button should be disabled due to invalid date
    expect(submitButton.attributes('disabled')).toBeDefined();
  });

  it('validates button state with recurring request fields', async () => {
    const submitButton = wrapper.find('button[type="submit"]');
    
    // Fill initial required fields
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    await wrapper.find('#startDate').setValue(startDate.toISOString().split('T')[0]);
    await wrapper.find('#reason').setValue('Test recurring WFH request');
    await wrapper.find('#fullDay').setValue('FULL_DAY');
    
    // Enable recurring without end date
    await wrapper.find('#recurring').setValue(true);
    await wrapper.vm.$nextTick();
    
    // Button should be disabled without end date
    expect(submitButton.attributes('disabled')).toBeDefined();

    // Add valid end date
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + 5);
    await wrapper.find('#endDate').setValue(endDate.toISOString().split('T')[0]);
    await wrapper.vm.$nextTick();
    
    // Button should now be enabled
    expect(submitButton.attributes('disabled')).toBeUndefined();

    // Test with invalid end date
    const invalidEndDate = new Date(startDate);
    invalidEndDate.setDate(startDate.getDate() - 1);
    await wrapper.find('#endDate').setValue(invalidEndDate.toISOString().split('T')[0]);
    await wrapper.vm.$nextTick();
    
    // Button should be disabled with invalid end date
    expect(submitButton.attributes('disabled')).toBeDefined();
  });
});
