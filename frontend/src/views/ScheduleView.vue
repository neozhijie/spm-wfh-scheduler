<template>
  <div id="app">
    <Navbar />
    <div class="dashboard-container">
      <div class="main-section">
        <div class="calendar-container">
          <FullCalendar 
            :options="calendarOptions"
          />
          <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
          </div>
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

    // Clear existing events before pushing new ones
    const newEvents = [];

    fetchedDates.forEach(dateObj => {
      const eventDate = dateObj.date;
      const wfhStatus = dateObj.schedule;

      if (wfhStatus === 'AM') {
        newEvents.push({
          title: 'WFH (AM)',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T13:00:00`,
          backgroundColor: '#FFD93D',
        });
      } else if (wfhStatus === 'PM') {
        newEvents.push({
          title: 'WFH (PM)',
          start: `${eventDate}T14:00:00`,
          end: `${eventDate}T18:00:00`,
          backgroundColor: '#FFD93D',
        });
      } else if (wfhStatus === 'FullDay') {
        newEvents.push({
          title: 'WFH (Full Day)',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T18:00:00`,
          backgroundColor: '#FFD93D',
          color: 'black'
        });
      } else if (wfhStatus === 'FullDayPending') {
        newEvents.push({
          title: 'Pending WFH (Full Day)',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T18:00:00`,
          backgroundColor: '#141b4d'
        });
      } else if (wfhStatus === 'AMPending') {
        newEvents.push({
          title: 'Pending WFH (AM)',
          start: `${eventDate}T09:00:00`,
          end: `${eventDate}T13:00:00`,
          backgroundColor: '#141b4d'
        });
      } else if (wfhStatus === 'PMPending') {
        newEvents.push({
          title: 'Pending WFH (PM)',
          start: `${eventDate}T14:00:00`,
          end: `${eventDate}T18:00:00`,
          backgroundColor: '#141b4d'
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

    container.style.borderRadius = '4px';
    container.style.margin = '1px 0';
    container.style.padding = '2px 4px';
    container.style.fontSize = '0.8em';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.backgroundColor = arg.event.backgroundColor || '#3788d8';

    const title = document.createElement('span');
    title.textContent = arg.event.title;
    title.style.fontWeight = 'bold';
    title.style.fontSize = '12px';
    if (arg.event.backgroundColor === '#FFD93D') {
      title.style.color = 'black';
    } else {
      title.style.color = 'white';
    }


    container.appendChild(title);

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

  isLoading.value = false;
  
  // Load past 2 and next 3 months together
  const promises = [];
  for (let i = 1; i < ranges.length; i++) {
    promises.push(fetchEvents(ranges[i].start, ranges[i].end));
  }

  // Wait for all past and future month events to load
  await Promise.all(promises);

}

</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
}

.main-section {
  display: flex;
  justify-content: center;
  flex: 1;
  width: 100%;
  position: relative;
}

.calendar-container {
  width: 100%;
  max-width: 1200px; /* Add maximum width */
  margin: 0 auto;
  padding: 1rem;
  position: relative;
}

/* Calendar specific styles */
:deep(.fc) {
  width: 100%;
  height: 100%;
  min-height: 600px;
}

:deep(.fc-toolbar-title) {
  font-size: 1.2em !important;
}

:deep(.fc-daygrid-event) {
  white-space: normal !important;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block !important;
  margin: 1px 2px !important;
}

:deep(.fc-event-title) {
  padding: 0 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.85em;
}

/* Loading overlay styles */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 2s linear infinite;
}

/* Media Queries */
@media screen and (max-width: 768px) {
  :deep(.fc-header-toolbar) {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  :deep(.fc-toolbar-title) {
    font-size: 1em !important;
    margin: 0.5rem 0 !important;
  }

  :deep(.fc-button) {
    padding: 0.2rem 0.5rem !important;
    font-size: 0.9em !important;
  }

  .calendar-container {
    padding: 0.5rem;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>


