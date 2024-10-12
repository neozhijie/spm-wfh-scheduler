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
const isLoading = ref(false);

// User data from local storage
onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
  }
  initiateChunkedSummaryLoading(); // Fetch events on mount
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
async function fetchEvents(startDate, endDate) {
  try {
    const startDateStr = startDate.toISOString().split('T')[0];
    const endDateStr = endDate.toISOString().split('T')[0];
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/personal-schedule/${user.value.staff_id}`, {
      params: {
        start_date: startDateStr,
        end_date: endDateStr
      }
    });
    const fetchedDates = response.data.dates;
    console.log(response.data);

    // Clear existing events before pushing new ones
    const newEvents = [];

    fetchedDates.forEach(dateObj => {
      const eventDate = dateObj.date;
      const wfhStatus = dateObj.schedule;

      if (wfhStatus === 'AM') {
        newEvents.push({
          title: 'WFH AM',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T13:00:00`
        });
      } else if (wfhStatus === 'PM') {
        newEvents.push({
          title: 'WFH PM',
          start: `${eventDate}T14:00:00`,
          end: `${eventDate}T18:00:00`
        });
      } else if (wfhStatus === 'FullDay') {
        newEvents.push({
          title: 'WFH Full Day',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T18:00:00`
        });
      } else if (wfhStatus === 'FullDayPending') {
        newEvents.push({
          title: 'Pending WFH Full Day',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T18:00:00`,
          backgroundColor: '#FFA500'
        });
      } else if (wfhStatus === 'AMPending') {
        newEvents.push({
          title: 'Pending WFH AM',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T13:00:00`,
          backgroundColor: '#FFA500'
        });
      } else if (wfhStatus === 'PMPending') {
        newEvents.push({
          title: 'Pending WFH PM',
          start: `${eventDate}T14:00:00`,
          end: `${eventDate}T18:00:00`,
          backgroundColor: '#FFA500'
        });
      } 
    });

    // Update the reactive events array
    events.value.push(...newEvents); 

  } catch (error) {
    console.error('Error fetching events:', error);
  }
}

// Calendar options
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
  weekends: false,
  events: events.value,  // Make sure this is reactive
  eventContent: function(arg) {
  const container = document.createElement('div');
  container.style.display = 'flex';
  container.style.flexDirection = 'column';
  container.style.justifyContent = 'center';
  container.style.alignItems = 'center';
  container.style.padding = '5px';
  container.style.backgroundColor = arg.event.backgroundColor || '#3788d8';

  // Create a title element and add it to the container
  const title = document.createElement('span');
  title.textContent = arg.event.title; // The event title
  title.style.fontWeight = 'bold';
  title.style.fontSize = '12px';
  title.style.color = 'white';
  
  container.appendChild(title);

  // If there's extendedProps for timeOfDay, display it too
  if (arg.event.extendedProps.timeOfDay) {
    const timeOfDay = document.createElement('span');
    timeOfDay.textContent = arg.event.extendedProps.timeOfDay;
    timeOfDay.style.fontSize = '10px';
    timeOfDay.style.color = 'lightgray';
    container.appendChild(timeOfDay);
  }

  return { domNodes: [container] };
},
  eventClassNames:'calendar-event',
  allDaySlot: false,
  slotMinTime: '09:00:00',
  slotMaxTime: '19:00:00',
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

async function initiateChunkedSummaryLoading() {
  isLoading.value = true;
  const today = new Date();

  // Define the date ranges
  const ranges = [];

  // Current month
  const currentMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  const currentMonthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  ranges.push({ start: currentMonthStart, end: currentMonthEnd });

  // Past 2 months
  for (let i = 1; i <= 2; i++) {
    const start = new Date(today.getFullYear(), today.getMonth() - i, 1);
    const end = new Date(today.getFullYear(), today.getMonth() - i + 1, 0);
    ranges.push({ start, end });
  }

  // Next 3 months
  for (let i = 1; i <= 3; i++) {
    const start = new Date(today.getFullYear(), today.getMonth() + i, 1);
    const end = new Date(today.getFullYear(), today.getMonth() + i + 1, 0);
    ranges.push({ start, end });
  }

  // Load the current month events first
  await fetchEvents(ranges[0].start, ranges[0].end);

  // Load past 2 and next 3 months together
  const promises = [];
  for (let i = 1; i < ranges.length; i++) {
    promises.push(fetchEvents(ranges[i].start, ranges[i].end));
  }

  // Wait for all past and future month events to load
  await Promise.all(promises);

  isLoading.value = false;
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
