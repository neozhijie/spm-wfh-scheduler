import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import RequestView from '../views/RequestView.vue';
import axios from 'axios';
import { format } from 'date-fns';
import Navbar from '@/components/Navbar.vue';

vi.mock('axios');
vi.mock('date-fns', () => ({
  format: vi.fn((date, formatStr) => '2024-10-30'),
  isValid: vi.fn(() => true)
}));

describe('RequestView.vue', () => {
  let wrapper;
  const mockUser = {
    staff_id: 1,
    staff_fname: 'John',
    staff_lname: 'Doe'
  };

  const mockPendingRequests = [
    {
      request_id: 1,
      staff_id: 2,
      request_date: '2024-10-30',
      start_date: '2024-11-01',
      end_date: '2024-11-02',
      reason_for_applying: 'Test reason',
      duration: 'FULL_DAY',
      is_recurring: true
    }
  ];

  const mockStaffResponse = {
    staff_fname: 'Jane',
    staff_lname: 'Smith'
  };

  beforeEach(() => {
    // Mock localStorage
    global.localStorage = {
      getItem: vi.fn(() => JSON.stringify(mockUser)),
      setItem: vi.fn(),
      clear: vi.fn()
    };

    // Mock axios responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/pending-requests')) {
        return Promise.resolve({ data: mockPendingRequests });
      }
      if (url.includes('/api/staff')) {
        return Promise.resolve({ data: mockStaffResponse });
      }
      return Promise.reject(new Error('Not found'));
    });

    // Mount component
    wrapper = mount(RequestView, {
      global: {
        components: { Navbar },
        stubs: ['Navbar']
      }
    });
  });

  afterEach(() => {
    wrapper.unmount();
    vi.clearAllMocks();
  });

  it('initializes with correct data from localStorage', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.user).toEqual(mockUser);
  });

  it('fetches and displays pending requests', async () => {
    await wrapper.vm.$nextTick();
    expect(axios.get).toHaveBeenCalled();
    expect(wrapper.vm.pendingRequests).toEqual(mockPendingRequests);
    expect(wrapper.find('table').exists()).toBe(true);
  });

  it('formats dates correctly', async () => {
    await wrapper.vm.$nextTick();
    const formattedDate = wrapper.vm.formatDate('2024-10-30');
    expect(formattedDate).toBeDefined();
    expect(format).toHaveBeenCalled();
  });

  it('displays staff names correctly', async () => {
    await wrapper.vm.$nextTick();
    const staffName = await wrapper.vm.getNameById(2);
    expect(staffName).toBe('Jane Smith');
    expect(wrapper.vm.staffNames[2]).toBe('Jane Smith');
  });

  it('handles approve request flow', async () => {
    await wrapper.vm.$nextTick();
    
    // Click approve button
    await wrapper.find('.btn-approve').trigger('click');
    expect(wrapper.vm.showApproveConfirmation).toBe(true);
    expect(wrapper.vm.requestToApprove).toBeDefined();

    // Confirm approval
    await wrapper.vm.confirmApprove();
    expect(axios.patch).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_URL}/api/update-request`,
      {
        request_id: mockPendingRequests[0].request_id,
        request_status: 'APPROVED',
        reason: ''
      }
    );
  });

  it('handles reject request flow', async () => {
    await wrapper.vm.$nextTick();
    
    // Open reject form
    await wrapper.find('.btn-rej').trigger('click');
    expect(wrapper.vm.showForm).toBe(true);
    expect(wrapper.vm.selectedRequest).toBeDefined();

    // Fill rejection reason
    wrapper.vm.rej_reason = 'Test rejection reason';

    // Submit rejection
    await wrapper.vm.rejectRequest();
    expect(axios.patch).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_URL}/api/update-request`,
      {
        request_id: mockPendingRequests[0].request_id,
        request_status: 'REJECTED',
        reason: 'Test rejection reason'
      }
    );
  });

  it('validates rejection reason', async () => {
    await wrapper.vm.$nextTick();
    
    // Open reject form
    await wrapper.find('.btn-rej').trigger('click');
    
    // Try to submit without reason
    await wrapper.vm.rejectRequest();
    expect(wrapper.vm.errorMessage).toBe('Please provide a reason for rejection.');
    expect(axios.patch).not.toHaveBeenCalled();
  });

  it('displays correct badges for request types', async () => {
    await wrapper.vm.$nextTick();
    
    const badges = wrapper.findAll('.badge');
    expect(badges.length).toBeGreaterThan(0);
    
    // Check recurring badge
    const recurringBadge = wrapper.find('.badge.bg-info');
    expect(recurringBadge.exists()).toBe(true);
    expect(recurringBadge.text()).toBe('Recurring');

    // Check duration badge
    const durationBadge = wrapper.find('.badge.bg-success');
    expect(durationBadge.exists()).toBe(true);
    expect(durationBadge.text()).toBe('FULL DAY');
  });

  it('handles API errors gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    // Mock API error
    axios.get.mockRejectedValueOnce(new Error('API Error'));
    
    await wrapper.vm.fetchPendingRequests();
    
    expect(consoleSpy).toHaveBeenCalled();
    expect(alertMock).toHaveBeenCalledWith('Error fetching pending requests');
  });

  it('closes forms correctly', async () => {
    await wrapper.vm.$nextTick();
    
    // Open and close reject form
    await wrapper.find('.btn-rej').trigger('click');
    expect(wrapper.vm.showForm).toBe(true);
    
    await wrapper.vm.closeForm();
    expect(wrapper.vm.showForm).toBe(false);
    expect(wrapper.vm.rej_reason).toBe('');
    expect(wrapper.vm.errorMessage).toBe('');

    // Open and close approve confirmation
    await wrapper.find('.btn-approve').trigger('click');
    expect(wrapper.vm.showApproveConfirmation).toBe(true);
    
    await wrapper.vm.closeApproveConfirmation();
    expect(wrapper.vm.showApproveConfirmation).toBe(false);
    expect(wrapper.vm.requestToApprove).toBe(null);
  });

  it('handles form validation for rejection reason', async () => {
    await wrapper.vm.$nextTick();
    
    // Open reject form
    await wrapper.find('.btn-rej').trigger('click');
    
    // Test empty reason
    wrapper.vm.rej_reason = '';
    await wrapper.vm.rejectRequest();
    expect(wrapper.vm.errorMessage).toBe('Please provide a reason for rejection.');
    
    // Test whitespace-only reason
    wrapper.vm.rej_reason = '   ';
    await wrapper.vm.rejectRequest();
    expect(wrapper.vm.errorMessage).toBe('Please provide a reason for rejection.');
    
    // Test valid reason
    wrapper.vm.rej_reason = 'Valid reason';
    await wrapper.vm.rejectRequest();
    expect(wrapper.vm.errorMessage).toBe('');
  });

  it('handles API errors during approval/rejection', async () => {
    await wrapper.vm.$nextTick();
    
    // Mock API error
    const errorMessage = 'API Error';
    axios.patch.mockRejectedValueOnce(new Error(errorMessage));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    // Try to approve
    await wrapper.find('.btn-approve').trigger('click');
    await wrapper.vm.confirmApprove();

    expect(consoleSpy).toHaveBeenCalled();
    expect(alertMock).toHaveBeenCalledWith('Error approving request');

    // Reset mocks
    consoleSpy.mockClear();
    alertMock.mockClear();

    // Mock API error with response message
    axios.patch.mockRejectedValueOnce({
      response: { data: { message: 'Custom error message' } }
    });

    // Try to approve again
    await wrapper.find('.btn-approve').trigger('click');
    await wrapper.vm.confirmApprove();

    expect(alertMock).toHaveBeenCalledWith('Error approving request: Custom error message');
  });

  it('maintains form state during rejection process', async () => {
    await wrapper.vm.$nextTick();
    
    // Open reject form
    await wrapper.find('.btn-rej').trigger('click');
    
    // Set rejection reason
    wrapper.vm.rej_reason = 'Test reason';
    
    // Mock API error
    axios.patch.mockRejectedValueOnce(new Error('API Error'));
    
    // Try to reject
    await wrapper.vm.rejectRequest();
    
    // Form should still be open with the same reason
    expect(wrapper.vm.showForm).toBe(true);
    expect(wrapper.vm.rej_reason).toBe('Test reason');
  });
});
