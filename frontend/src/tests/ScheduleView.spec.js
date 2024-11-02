import { mount } from '@vue/test-utils';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import ScheduleView from '../views/ScheduleView.vue';
import axios from 'axios';
import FullCalendar from '@fullcalendar/vue3';
import Navbar from '@/components/Navbar.vue';

// Mock FullCalendar
vi.mock('@fullcalendar/vue3', () => ({
  default: {
    name: 'FullCalendar',
    props: ['options'],
    template: '<div class="mock-calendar"></div>'
  }
}));

// Mock axios
vi.mock('axios');

describe('ScheduleView.vue', () => {
  let wrapper;
  const mockUser = {
    staff_id: 1,
    staff_fname: 'John',
    staff_lname: 'Doe'
  };

  const mockEvents = {
    dates: [
      { date: '2024-10-30', schedule: 'FullDay' },
      { date: '2024-10-31', schedule: 'AM' },
      { date: '2024-11-01', schedule: 'PMPending' }
    ]
  };

  beforeEach(() => {
    // Mock localStorage
    global.localStorage = {
      getItem: vi.fn(() => JSON.stringify(mockUser)),
      setItem: vi.fn(),
      clear: vi.fn()
    };

    // Mock successful axios response
    axios.get.mockResolvedValue({ data: mockEvents });

    // Mount component with composition API support
    wrapper = mount(ScheduleView, {
      global: {
        components: {
          FullCalendar,
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

  it('initializes with correct user data from localStorage', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.user).toEqual(mockUser);
  });

  it('fetches and processes events correctly', async () => {
    await wrapper.vm.$nextTick();
    
    // Verify API call
    expect(axios.get).toHaveBeenCalled();
    
    // Wait for events to be processed
    await wrapper.vm.$nextTick();
    
    // Access events through the component instance
    const events = wrapper.vm.events;
    expect(events.length).toBeGreaterThan(0);
    
    // Verify event formatting
    const fullDayEvent = events.find(e => e.title === 'WFH (Full Day)');
    expect(fullDayEvent).toBeDefined();
    expect(fullDayEvent.backgroundColor).toBe('#FFD93D');
  });

  it('handles date click within valid range', async () => {
    const validDate = new Date().toISOString().split('T')[0];
    await wrapper.vm.handleDateClick({ dateStr: validDate });
    expect(wrapper.vm.selectedDate).toBe(validDate);
  });

  it('prevents selection of dates outside valid range', async () => {
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    // Test past date
    const pastDate = new Date();
    pastDate.setMonth(pastDate.getMonth() - 3);
    await wrapper.vm.handleDateClick({ dateStr: pastDate.toISOString().split('T')[0] });
    expect(alertMock).toHaveBeenCalledWith('You cannot select a date before two months ago.');
  });

  it('handles API errors gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    axios.get.mockRejectedValueOnce(new Error('API Error'));
    
    await wrapper.vm.fetchEvents(new Date(), new Date());
    expect(consoleSpy).toHaveBeenCalled();
  });

  it('correctly configures calendar options', async () => {
    await wrapper.vm.$nextTick();
    const options = wrapper.vm.calendarOptions;
    
    expect(options.initialView).toBe('dayGridMonth');
    expect(options.weekends).toBe(false);
    expect(options.businessHours).toBeDefined();
  });

  it('processes different event types correctly', async () => {
    const mockEventsWithTypes = {
      dates: [
        { date: '2024-10-30', schedule: 'FullDay' },
        { date: '2024-10-31', schedule: 'AM' },
        { date: '2024-11-01', schedule: 'PM' }
      ]
    };

    axios.get.mockResolvedValueOnce({ data: mockEventsWithTypes });
    await wrapper.vm.fetchEvents(new Date(), new Date());
    await wrapper.vm.$nextTick();

    const events = wrapper.vm.events;
    expect(events.some(e => e.title === 'WFH (Full Day)')).toBe(true);
    expect(events.some(e => e.title === 'WFH (AM)')).toBe(true);
    expect(events.some(e => e.title === 'WFH (PM)')).toBe(true);
  });

  it('handles chunked loading of events correctly', async () => {
    await wrapper.vm.initiateChunkedSummaryLoading();
    await wrapper.vm.$nextTick();

    // Should make multiple calls for different date ranges
    expect(axios.get).toHaveBeenCalled();
    expect(wrapper.vm.isLoading).toBe(false);
  });

  it('validates date ranges correctly', async () => {
    await wrapper.vm.$nextTick();
    const minDate = wrapper.vm.computeMinDate;
    const maxDate = wrapper.vm.computeMaxDate;

    expect(minDate instanceof Date).toBe(true);
    expect(maxDate instanceof Date).toBe(true);
  });

  it('handles empty event responses correctly', async () => {
    axios.get.mockResolvedValueOnce({ data: { dates: [] } });
    wrapper.vm.events = [];
    await wrapper.vm.fetchEvents(new Date(), new Date());
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.events.length).toBe(0);
  });
});
