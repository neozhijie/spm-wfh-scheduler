<template>
  <div id="app">
    <Navbar />
    <div class="dashboard-container">
      <div class="top-section">
        <h1>Welcome to your Schedule Dashboard</h1>
        <p>You are logged in as {{ user.staff_fname }} {{ user.staff_lname }}</p>
      </div>

      <div class="main-section">
        <div class="calendar-container">
          <FullCalendar 
            :options="calendarOptions"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Navbar from '@/components/Navbar.vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import axios from 'axios';

const user = ref({});
const selectedDate = ref('');
const events = ref([]); // Reactive array to hold events

// User data from local storage
onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
  }
  fetchEvents(); // Fetch events on mount
});

// Computed properties for valid date range
const computeMinDate = computed(() => {
  const date = new Date();
  date.setMonth(date.getMonth() - 2);
  return date;
});

const computeMaxDate = computed(() => {
  const date = new Date();
  date.setMonth(date.getMonth() + 3);
  return date;
});

// Function to fetch events from the backend
async function fetchEvents() {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/`); // Replace with backend API endpoint
    const fetchedDates = response.data; 
    console.log(response.data);

    fetchedDates.forEach(dateObj => {
      const eventDate = dateObj.date;
      const wfhStatus = dateObj.wfh;

      if (wfhStatus === 'AM') {
        events.value.push({
          title: 'WFH AM',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T13:00:00`
        });
      } else if (wfhStatus === 'PM') {
        events.value.push({
          title: 'WFH PM',
          start: `${eventDate}T14:00:00`,
          end: `${eventDate}T18:00:00`
        });
      } else if (wfhStatus === 'FullDay') {
        events.value.push({
          title: 'WFH Full Day',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T18:00:00`
        });
      }
    });
  } catch (error) {
    console.error('Error fetching events:', error);
  }
}

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  dateClick: handleDateClick,
  selectable: true,
  validRange: {
    start: computeMinDate.value,
    end: computeMaxDate.value,
  },
  events: events.value,
  eventClassNames: 'calendar-event',
  allDaySlot: false,
  slotMinTime: '09:00:00',
  slotMaxTime: '18:00:00',
  businessHours: {
    startTime: '09:00',
    endTime: '18:00',
    daysOfWeek: [1, 2, 3, 4, 5],
  },

}));



// Handle date click event
async function handleDateClick(info) {
  const clickedDate = new Date(info.dateStr);

  if (clickedDate < computeMinDate.value) {
    alert('You cannot select a date before two months ago.');
  } else if (clickedDate > computeMaxDate.value) {
    alert('You cannot select a date beyond three months ahead.');
  } else {
    console.log('Date clicked:', info.dateStr);
    selectedDate.value = info.dateStr;
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.top-section {
  padding: 2rem;
  text-align: left;
}

.main-section {
  display: flex;
  justify-content: center;
  height: 100%;
}

.calendar-container {
  width: 85%; 
  padding: 1rem;
}

.fc {
  width: 100%;
  height: 100%;
}


</style>
