<template>
  <div class="login-container">
    <div class="form-container">
      <div class="form-field">
        <label for="date">Date:
          <input type="text" v-model="selectedDate" readonly placeholder="Select a date" class="input-field" />
          <span class="calendar-icon" @click="toggleCalendar">&#128197;</span> <!-- Calendar icon -->
        </label>
      </div>
      <div class="form-field"> <!-- recurring option -->
        <label>
          <input type="radio" value="single" v-model="recurringOption" /> Single Day <!-- default -->
        </label>
        <label>
          <input type="radio" value="recurring" v-model="recurringOption" /> Recurring
        </label>
      </div>
      <div class="form-field" v-if="recurringOption === 'recurring'"> <!-- recurring option -->
        <label for="dayOfWeek">Day of the Week:
          <select class="input-field" v-model="selectedDayOfWeek">
            <option value="mon">Monday</option>
            <option value="tue">Tueday</option>
            <option value="wed">Wednesday</option>
            <option value="thu">Thursday</option>
            <option value="fri">Friday</option>
            <option value="sat">Saturday</option>
            <option value="sun">Sunday</option>
          </select>
        </label>
      </div>
      <div class="form-field">
        <label for="reasons">Reasons:
          <input type="text" v-model="reasons" placeholder="Enter reasons" class="input-field" />
        </label>
      </div>
      <button @click="applyDate" class="apply-button">Apply</button>
    </div>

    <!-- Calendar popup when icon is clicked -->
    <div v-if="showCalendar" class="calendar-popup">
      <FullCalendar :options="calendarOptions" @dateClick="handleDateClick" />
    </div>
    <div v-if="showCalendar" class="calendar-popup">
      <button class="close-button" @click="closeCalendar">X</button>
      <FullCalendar :options="calendarOptions" />
    </div>
  </div>
</template>

  
  
    
<script>
import { defineComponent, ref } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';

export default defineComponent({
  components: {
    FullCalendar,
  },
  setup() {
    const selectedDate = ref(null);

    const isRecurring = ref(false);
    const selectedDayOfWeek = ref("Monday"); 
    const recurringOption = ref("single");

    const reasons = ref("");
    const showCalendar = ref(false);

    const today = new Date();
    const twoMonthsAgo = new Date();
    const threeMonthsAhead = new Date();

    twoMonthsAgo.setMonth(today.getMonth() - 2);
    threeMonthsAhead.setMonth(today.getMonth() + 3);

    const calendarOptions = {
      plugins: [dayGridPlugin, interactionPlugin],
      initialView: 'dayGridMonth',
      selectable: true,
      validRange: {
        start: twoMonthsAgo.toISOString().split('T')[0],  // Format as YYYY-MM-DD
        end: threeMonthsAhead.toISOString().split('T')[0]
      },
      dateClick: handleDateClick,
    };

    function handleDateClick(info) {
      const clickedDate = new Date(info.dateStr);
      if (clickedDate >= twoMonthsAgo && clickedDate <= threeMonthsAhead) {
        selectedDate.value = selectedDate.value === info.dateStr ? null : info.dateStr;
        closeCalendar();
        showModal.value = true;  // Show the modal after clicking a valid date
  
      } else {
        alert("Date is out of the allowed range!");
      }
    }


    function toggleCalendar() {
      showCalendar.value = !showCalendar.value; // Toggle calendar visibility
    }

    function closeCalendar() {
      showCalendar.value = false; // Close the calendar popup
    }

    function getRecurringDates(dayOfWeek) {
      // compute recurring dates for selectedDayOfWeek for next 3 mths

      const recurringDates = [];
      let currentDate = new Date();

      // e.g. if today is WED (currentDate.getDay()=3)
      // and user selects MON (dayOfWeek=1),
      // the immediate recurring date will be 5 days from today
      let dayOffset = (dayOfWeek + 7 - currentDate.getDay()) % 7;
        // %7 keeps the offset within 0-6 days

      // set currentDate to the first recurrence of selectedDayOfWeek
      currentDate.setDate(currentDate.getDate() + dayOffset);

      while (currentDate <= threeMonthsAhead) {
        recurringDates.push(currentDate.toISOString().split('T')[0]); // Format YYYY-MM-DD
        currentDate.setDate(currentDate.getDate() + 7); // Move to the next week
      }

      return recurringDates;
    }

    function applyDate() {
      // validations
      if (!reasons.value) { alert('Provide a reason.'); return; }

      // single-day arrangement
      if (recurringOption.value === 'single' && selectedDate.value) {
        fetchDates([selectedDate.value], false);
      }
      // recurring arrangement
      else if (recurringOption.value === 'recurring' && selectedDate.value) {
        const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

        // takes the index day that matches the selected day in form
        const selectedDay = daysOfWeek.indexOf(selectedDayOfWeek.value);
        const recurringDates = getRecurringDates(selectedDay);
        fetchDates(recurringDates, true);
      }

      function fetchDates(dates, isRecurring) {
        fetch(`${import.meta.env.VITE_API_URL}/api/save-date/${userData.staff_id}`, { // to integrate with backend over here 
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dates: dates, // local var
            recurring: isRecurring, // local var
            reasons: reasons.value,
          }),
        })
          .then(response => response.json())
          .then(data => {
            // const dateObj = new Date(selectedDate.value);
            // const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            // const dayName = daysOfWeek[dateObj.getDay()];

            if (isRecurring) {
              alert(`${selectedDayOfWeek.value} applied recurring successfully`);
            } else {
              alert(`${dates[0]} applied successfully`);
            }
            closeModal(); // Close the modal after applying the date
          })
          .catch(error => {
            console.error('Error:', error);
          });
      }
    }

      

    return {
      selectedDate,
      isRecurring,
      reasons,
      showCalendar,
      calendarOptions,
      toggleCalendar,
      closeCalendar,
      handleDateClick,
      applyDate,

      selectedDay,
      fetchDates,
    };
  },
});
</script>

    
  <style>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('@/assets/images/login-image.jpg');
    background-size: cover;
    background-position: center;
  }
  
  .form-container {
    background-color: white; /* Ensures that the form has a visible background */
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 400px; /* Set a fixed width for better alignment */
  }
  
  .form-field {
    margin-bottom: 15px; /* Space between each field */
    display: flex;
    flex-direction: column; /* Arrange label and input vertically */
  }
  
  .input-field {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  .calendar-icon {
    cursor: pointer;
    margin-top: 5px; /* Space above the icon */
    font-size: 20px; /* Adjust size as needed */
  }
  
  .apply-button {
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .apply-button:hover {
    background-color: #0056b3; /* Darker blue on hover */
  }
  
  /* Calendar popup styles */
  .calendar-popup {
  position: absolute; 
  top: 50%; 
  left: 50%; 
  transform: translate(-50%, -50%); 
  width: 500px; 
  height: 450px; /* Set fixed height */
  overflow: hidden; 
  background-color: white; 
  border: 1px solid #ccc; 
  border-radius: 8px; 
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); 
  z-index: 1000; 
}

.fc {
  height: 100%; 
}

.fc-daygrid {
  height: 100%; 
}

.fc-daygrid-day {
  height: 50px; /* Set fixed height for each day */
  min-height: 50px; /* Ensure a minimum height */
}


  </style>
  