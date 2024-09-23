<template>
    <div class="login-container">
      <div class="calendar-container">
      <FullCalendar :options="calendarOptions" />
      <div v-if="selectedDate" class="info-card">
        <p>Selected Date: <span>{{ selectedDate }}</span></p>
        <label>
          <input type="checkbox" v-model="isRecurring" /> Recurring
        </label>
        <button @click="applyDate">Apply</button>
      </div>
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
  
      // Calculate the valid range: two months back and three months forward
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
        } else {
          alert("Date is out of the allowed range!");
        }
      }
  
      function applyDate() {
        if (selectedDate.value) {
          fetch('http://localhost:5000/api/save-date', { // to integrate with backend over here 
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              date: selectedDate.value,
              recurring: isRecurring.value,
            }),
          })
          .then(response => response.json())
          .then(data => {
            const dateObj = new Date(selectedDate.value);
            const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const dayName = daysOfWeek[dateObj.getDay()];
  
            if (isRecurring.value) {
              alert(`${dayName} applied recurring successfully`);
            } else {
              alert(`${selectedDate.value} applied successfully`);
            }
          })
          .catch(error => {
            console.error('Error:', error);
          });
        }
      }
  
      return {
        selectedDate,
        isRecurring,
        calendarOptions,
        handleDateClick,
        applyDate,
      };
    },
  });
  
  </script>
  
  <style>
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
  
  .info-card {
    max-width: 900px;
    margin: 20px auto;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #f9f9f9;
  }

  .calendar-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 50vw;
    height: 80vh;
    background-color: white; /* Ensures that the calendar has a visible background */
    border: 1px solid #ccc;
  } 
  
  /* Forces FullCalendar to fill its container */
  .fc {
    width: 80%;
    height: 81%;
  }
  
  
  button {
    margin-top: 10px;
  }
  /* Customize calendar header */
  .fc-toolbar.fc-header-toolbar {
    /* background-color: #3f51b5; */
    color: black;
  }
  
  /* Customize day numbers */
  .fc-daygrid-day-number {
    color: #e91e63;
  }
  
  /* Customize background of all days */
  .fc-daygrid-day {
    background-color: #e0f7fa;
  }
  
  /* Today's date */
  .fc-day-today {
    background-color: #ffeb3b !important;
    color: black;
  }
  </style>
  