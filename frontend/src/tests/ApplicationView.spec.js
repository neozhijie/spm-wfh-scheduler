import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ApplicationView from '@/views/ApplicationView.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios')

// Mock localStorage
const mockLocalStorage = {
  user: JSON.stringify({
    staff_id: 11,
    reporting_manager: 9,
    dept: 'Sales',
    position: 'Account Manager'
  })
}

const mockDate = new Date('2024-01-15')
vi.setSystemTime(mockDate)

describe('ApplicationView.vue', () => {
  let wrapper

  beforeEach(() => {
    // Clear mocks
    vi.clearAllMocks()
    
    // Mock localStorage
    global.localStorage = {
      getItem: vi.fn((key) => mockLocalStorage[key]),
      setItem: vi.fn()
    }

    // Mount component
    wrapper = mount(ApplicationView, {
      global: {
        stubs: ['Navbar']
      }
    })
  })

  it('renders the form with all required elements', () => {
    expect(wrapper.find('h5').text()).toBe('Work From Home Request Form')
    expect(wrapper.find('#startDate').exists()).toBe(true)
    expect(wrapper.find('#reason').exists()).toBe(true)
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(3)
    expect(wrapper.find('#recurring').exists()).toBe(true)
  })

  it('validates start date is not on weekend', async () => {
    // Set a Saturday date
    await wrapper.find('#startDate').setValue('2024-01-13')
    
    expect(wrapper.vm.startDateError).toBe('Start date cannot be a weekend.')
  })

  it('handles recurring request toggle correctly', async () => {
    // Set valid start date first
    await wrapper.find('#startDate').setValue('2024-01-16')
    
    // Toggle recurring checkbox
    await wrapper.find('#recurring').setValue(true)
    
    expect(wrapper.find('#endDate').exists()).toBe(true)
    
    // Toggle off
    await wrapper.find('#recurring').setValue(false)
    expect(wrapper.find('#endDate').exists()).toBe(false)
  })

  it('validates date ranges for recurring requests', async () => {
    await wrapper.find('#startDate').setValue('2024-01-16')
    await wrapper.find('#recurring').setValue(true)
    await wrapper.find('#endDate').setValue('2024-01-15') // End date before start date

    expect(wrapper.vm.endDateError).toBe('End date must be after the start date.')
  })

  it('successfully submits a single day request', async () => {
    // Mock successful API response
    axios.post.mockResolvedValueOnce({ data: { message: 'Success' } })

    // Fill form
    await wrapper.find('#startDate').setValue('2024-01-16')
    await wrapper.find('#reason').setValue('Working on project')
    await wrapper.find('input[value="FULL_DAY"]').setValue(true)

    // Submit form
    await wrapper.find('form').trigger('submit')

    // Verify API call
    expect(axios.post).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        staff_id: 11,
        manager_id: 9,
        reason_for_applying: 'Working on project',
        date: '2024-01-16',
        duration: 'FULL_DAY',
        dept: 'Sales',
        position: 'Account Manager',
        end_date: null
      })
    )
  })

  it('successfully submits a recurring request', async () => {
    // Mock successful API response
    axios.post.mockResolvedValueOnce({ data: { message: 'Success' } })

    // Fill form
    await wrapper.find('#startDate').setValue('2024-01-16')
    await wrapper.find('#recurring').setValue(true)
    await wrapper.find('#endDate').setValue('2024-01-20')
    await wrapper.find('#reason').setValue('Regular WFH schedule')
    await wrapper.find('input[value="HALF_DAY_AM"]').setValue(true)

    // Submit form
    await wrapper.find('form').trigger('submit')

    // Verify API call
    expect(axios.post).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        staff_id: 11,
        manager_id: 9,
        reason_for_applying: 'Regular WFH schedule',
        date: '2024-01-16',
        duration: 'HALF_DAY_AM',
        end_date: '2024-01-20'
      })
    )
  })

  it('handles API errors during submission', async () => {
    // Mock API error
    const errorMessage = 'Request failed'
    axios.post.mockRejectedValueOnce({
      response: { data: { message: errorMessage } }
    })

    // Fill form
    await wrapper.find('#startDate').setValue('2024-01-16')
    await wrapper.find('#reason').setValue('Test request')
    await wrapper.find('input[value="FULL_DAY"]').setValue(true)

    // Mock window.alert
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {})

    // Submit form
    await wrapper.find('form').trigger('submit')

    // Verify error handling
    expect(alertMock).toHaveBeenCalledWith(`Error: ${errorMessage}`)
  })

  it('resets form after successful submission', async () => {
    // Mock successful API response
    axios.post.mockResolvedValueOnce({ data: { message: 'Success' } })

    // Fill form
    await wrapper.find('#startDate').setValue('2024-01-16')
    await wrapper.find('#reason').setValue('Test request')
    await wrapper.find('input[value="FULL_DAY"]').setValue(true)

    // Submit form
    await wrapper.find('form').trigger('submit')

    // Verify form reset
    expect(wrapper.vm.startDate).toBe('')
    expect(wrapper.vm.reason).toBe('')
    expect(wrapper.vm.dayType).toBe('')
    expect(wrapper.vm.isRecurring).toBe(false)
  })
})