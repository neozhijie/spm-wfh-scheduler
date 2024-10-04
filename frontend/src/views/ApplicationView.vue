<template>
  <div>
    <Navbar />
    <div class="background-container">
      <div class="container py-5">
        <div class="row justify-content-center">
          <div class="col-md-8">
            <div class="card custom-card">
              <div class="card-header">
                <h2 class="mb-0">Work From Home Request Form</h2>
              </div>
              <div class="card-body">
                <form @submit.prevent="submitForm">
                  <!-- Start Date Field -->
                  <div class="mb-4">
                    <label for="startDate" class="form-label">Start Date</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="fas fa-calendar-alt"></i></span>
                      <input
                        type="date"
                        class="form-control"
                        id="startDate"
                        v-model="startDate"
                        :min="minStartDate"
                        :max="maxDate"
                        required
                        @change="validateDates"
                      >
                    </div>
                    <div v-if="startDateError" class="text-danger mt-1">
                      {{ startDateError }}
                    </div>
                  </div>

                  <!-- Day Type Selection -->
                  <div class="mb-4">
                    <label class="form-label">Select Day Type</label>
                    <div>
                      <div class="form-check form-check-inline">
                        <input
                          class="form-check-input"
                          type="radio"
                          id="fullDay"
                          value="FULL_DAY"
                          v-model="dayType"
                          required
                        >
                        <label class="form-check-label" for="fullDay">Full Day</label>
                      </div>
                      <div class="form-check form-check-inline">
                        <input
                          class="form-check-input"
                          type="radio"
                          id="halfDayAm"
                          value="HALF_DAY_AM"
                          v-model="dayType"
                          required
                        >
                        <label class="form-check-label" for="halfDayAm">Half Day (AM)</label>
                      </div>
                      <div class="form-check form-check-inline">
                        <input
                          class="form-check-input"
                          type="radio"
                          id="halfDayPm"
                          value="HALF_DAY_PM"
                          v-model="dayType"
                          required
                        >
                        <label class="form-check-label" for="halfDayPm">Half Day (PM)</label>
                      </div>
                    </div>
                  </div>

                  <!-- Recurring Request Checkbox -->
                  <div class="mb-4 form-check">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      id="recurring"
                      v-model="isRecurring"
                      @change="handleRecurringChange"
                      :disabled="isRecurringDisabled"
                    >
                    <label class="form-check-label" for="recurring">Recurring Request</label>
                    <div v-if="showRecurringWarning" class="text-danger mt-1">
                      Please select a valid start date before making this a recurring request.
                    </div>
                  </div>

                  <!-- End Date Field (Conditional) -->
                  <div v-if="isRecurring" class="mb-4">
                    <label for="endDate" class="form-label">End Date</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="fas fa-calendar-alt"></i></span>
                      <input
                        type="date"
                        class="form-control"
                        id="endDate"
                        v-model="endDate"
                        :min="startDate"
                        :max="maxDate"
                        required
                        @change="validateDates"
                      >
                    </div>
                    <div v-if="endDateError" class="text-danger mt-1">
                      {{ endDateError }}
                    </div>
                  </div>

                  <!-- Reason Field -->
                  <div class="mb-4">
                    <label for="reason" class="form-label">Reason</label>
                    <textarea
                      class="form-control"
                      id="reason"
                      v-model="reason"
                      rows="3"
                      required
                    ></textarea>
                  </div>

                  <!-- Submit Button -->
                  <button
                    type="submit"
                    class="btn btn-primary btn-lg w-40"
                    :disabled="!isFormValid"
                  >
                    Submit Request
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import axios from 'axios';
import Navbar from '@/components/Navbar.vue'
import { ref } from 'vue';
const user = ref({});
const userData = JSON.parse(localStorage.getItem('user'));
export default {
  components: {
    Navbar
  },
  data() {
    return {
      startDate: '',
      endDate: '',
      isRecurring: false,
      showRecurringWarning: false,
      reason: '',
      startDateError: '',
      endDateError: '',
      dayType: ''
    }
  },
  computed: {
    minStartDate() {
      const date = new Date();
      date.setMonth(date.getMonth() - 2);
      return this.formatDate(date);
    },
    maxDate() {
      const date = new Date();
      date.setMonth(date.getMonth() + 3);
      return this.formatDate(date);
    },
    isRecurringDisabled() {
      return !this.startDate;
    },
    isFormValid() {
      return (
        this.startDate &&
        (!this.isRecurring || this.endDate) &&
        this.reason &&
        this.dayType &&
        !this.startDateError &&
        !this.endDateError
      );
    }
  },
  methods: {
    formatDate(date) {
      return date.toISOString().split('T')[0];
    },
    handleRecurringChange() {
      if (!this.startDate || this.startDateError) {
        this.showRecurringWarning = true;
        this.isRecurring = false;
      } else {
        this.showRecurringWarning = false;
        if (!this.isRecurring) {
          this.endDate = '';
        }
      }
      this.validateDates();
    },
    validateDates() {
      this.startDateError = '';
      this.endDateError = '';

      const startDate = new Date(this.startDate);
      const endDate = new Date(this.endDate);
      const minDate = new Date(this.minStartDate);
      const maxDate = new Date(this.maxDate);
      const twoMonthsAgo = new Date();
      twoMonthsAgo.setMonth(twoMonthsAgo.getMonth() - 2);
      const threeMonthsAhead = new Date();
      threeMonthsAhead.setMonth(threeMonthsAhead.getMonth() + 3);

      // Check if the start date is a weekend
      if (startDate.getDay() === 0 || startDate.getDay() === 6) {
        this.startDateError = 'Start date cannot be a weekend.';
      } else if (startDate < twoMonthsAgo) {
        this.startDateError = 'Start date cannot be more than 2 months ago.';
      } else if (startDate > threeMonthsAhead) {
        this.startDateError = 'Start date cannot be more than 3 months ahead.';
      } else if (startDate < minDate || startDate > maxDate) {
        this.startDateError = 'Start date must be within the allowed range.';
      }

      if (this.isRecurring) {
        if (endDate <= startDate) {
          this.endDateError = 'End date must be after the start date.';
        } else if (endDate < twoMonthsAgo) {
          this.endDateError = 'End date cannot be more than 2 months ago.';
        } else if (endDate > threeMonthsAhead) {
          this.endDateError = 'End date cannot be more than 3 months ahead.';
        } else if (endDate < minDate || endDate > maxDate) {
          this.endDateError = 'End date must be within the allowed range.';
        }
      }
    },
    async submitForm() {
    if (this.isFormValid) {
      // Prepare the data to send
      const requestData = {
        staff_id: userData.staff_id,
        manager_id: userData.reporting_manager,
        reason_for_applying: this.reason,
        date: this.startDate,
        duration: this.dayType,
        dept: userData.dept,
        position: userData.position,
        end_date: this.isRecurring ? this.endDate : null,
      };

      try {
        // Make the POST request
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/request`, requestData);

        // Success message
        console.log('Request successful:', response.data);
        alert('WFH request submitted successfully.');
        // Reset the form after submission
        this.resetForm();

      } catch (error) {
        // Handle errors (e.g., show error messages)
        console.error('Error submitting WFH request:', error.response.data);
        alert(`Error: ${error.response.data.message}`);
      }
    } else {
      // Shouldn't reach here since the button is disabled when form is invalid
      alert('Please fill out the form correctly.');
    }
  },
  resetForm() {
    this.startDate = '';
    this.endDate = '';
    this.isRecurring = false;
    this.reason = '';
    this.dayType = '';
    this.startDateError = '';
    this.endDateError = '';
    this.showRecurringWarning = false;
  },
  }
}
</script>

<style scoped>
.background-container {
  background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('@/assets/images/login-image.jpg');
  background-size: cover;
  background-position: center;
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
}

.custom-card {
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  border: none;
  border-radius: 15px;
  overflow: hidden;
}

.card-header {
  background-color: #141b4d;
  color: white;
  padding: 1.5rem;
  border-bottom: none;
}

.card-header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 0;
}

.card-body {
  padding: 2rem;
  background-color: #f8f9fa;
}

.form-label {
  font-weight: 600;
  color: #141b4d;
  margin-bottom: 0.5rem;
}

.form-control, .input-group-text {
  border-color: #d1d5db;
}

.form-control:focus {
  border-color: #141b4d;
  box-shadow: 0 0 0 0.2rem rgba(20, 27, 77, 0.25);
}

.input-group-text {
  background-color: #e9ecef;
  color: #141b4d;
}

.form-check-input:checked {
  background-color: #141b4d;
  border-color: #141b4d;
}

.form-check-label {
  margin-right: 1rem;
  color: #141b4d;
}

.btn-primary {
  background-color: #141b4d;
  border-color: #141b4d;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  transition: all 0.3s ease;
  display: block;
  margin: 0 auto;
}

.btn-primary:hover, .btn-primary:focus {
  background-color: #1e2a6d;
  border-color: #1e2a6d;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .card-header h2 {
    font-size: 1.5rem;
  }

  .card-body {
    padding: 1.5rem;
  }
}
</style>
