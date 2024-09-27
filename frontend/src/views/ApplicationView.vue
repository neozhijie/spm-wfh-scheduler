<template>
  <div class="login-container">
    <div class="calendar-container">
      <FullCalendar :options="calendarOptions" @dateClick="handleDateClick" />
      
      <!-- Modal Popup -->
      <div v-if="showModal" class="modal">
        <div class="modal-content">
          <span class="close" @click="closeModal">&times;</span>
          <p>Selected Date: <span>{{ selectedDate }}</span></p>
          <label>
            <input type="checkbox" v-model="isRecurring" /> Recurring
          </label>
          <label>
            Reasons: 
            <input type="text" v-model="reasons" placeholder="Enter reasons here" />
          </label>
          <button @click="applyDate">Apply</button>
        </div>
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
      const reasons = ref("");
      const showModal = ref(false); // Add this to manage modal visibility

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
          showModal.value = true;  // Show the modal after clicking a valid date
        } else {
          alert("Date is out of the allowed range!");
        }
      }

      function closeModal() {
        showModal.value = false; // Hide the modal
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
              reasons: reasons.value,
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
        calendarOptions,
        showModal, // Return the modal visibility
        handleDateClick,
        applyDate,
        closeModal, // Return the close modal function
      };
    },
  });
  </script>

  
  <style>
  .login-container {
      position: relative;
      height: 100vh;
      width: 100vw;
      display: flex;
      justify-content: center;
      align-items: center;
      background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('@/assets/images/login-image.jpg');
      background-size: cover;
      background-position: center;
    }
  .calendar-container {
    position: relative;
    /* display: flex; */
    justify-content: center;
    align-items: center;
    width: 50vw;
    height: 90vh;
    background-color: white; /* Ensures that the calendar has a visible background */
    border: 1px solid #ccc;
    } 

  .info-card {
    position: absolute;
    display: flex;
    flex-direction: row; /* Arrange items in a row */
    justify-content: center; /* Center the items horizontally */
    align-items: center; /* Align items vertically */
    gap: 20px; /* Add spacing between items */
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 80%; 
    height: 10vh;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #f9f9f9;
  }

    .modal {
    display: block;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5); /* Black background with opacity */
    justify-content: center;
    align-items: center;
  }

  .modal-content {
    background-color: white;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
    max-width: 500px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    text-align: center;
  }

  .close {
    position: absolute;
    top: 10px;
    right: 25px;
    font-size: 30px;
    font-weight: bold;
    cursor: pointer;
  }


  
  /* Forces FullCalendar to fill its container */
  .fc {
    width: 80%;
    height: 81%;
    margin-top: 20px;
    margin-left: auto;
    margin-right: auto
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
  