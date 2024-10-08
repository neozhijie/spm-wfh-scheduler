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
        <div class="right-container" :class="{'show': isRightContainerVisible }" v-html="rightContent">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Navbar from '@/components/Navbar.vue'
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import axios from 'axios';

const user = ref({});
const userData = JSON.parse(localStorage.getItem('user'))
const selectedDate = ref('');
const events = ref([]);
const rightContent = ref('');
const isRightContainerVisible = ref(false);

// User data from local storage
onMounted(() => {
  fetchStaffCounts(computeMinDate.value, computeMaxDate.value);
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

async function fetchStaffCounts(start, end) {
  const currentDate = new Date(start);
  const newEvents = [];

  while (currentDate <= end) {
    const dateStr = currentDate.toISOString().split('T')[0];
    
    try {
      // Replace this URL with your actual API endpoint

      const userData = JSON.parse(localStorage.getItem('user'));
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/manager-schedule-summary/${userData.staff_id}`)
      console.log(userData.staff_id)
      // console.log(userData)
      
      const count = response.data.wfh_count;
      const totalStaffs = response.data.total_staff;

      // Calculate percentage
      const percentage = ((count / totalStaffs) * 100).toFixed(2);

      // Create an event object with staff count
      newEvents.push({
        title: `${count} / ${totalStaffs} (${percentage}%)`,
        start: dateStr,
        end: dateStr,
        allDay: true,
        extendedProps: {
          staffCount: count,
          totalStaffs: totalStaffs,
          percentage: percentage,
        }
      });
    } catch (error) {
      console.error(`Failed to fetch staff count for ${dateStr}`, error);
    }

    currentDate.setDate(currentDate.getDate() + 1);
  }

  events.value = newEvents;
  await Vue.nextTick(() => {
    // Force re-render when events change
    calendarRef.value?.refetchEvents();
  });
}

// FullCalendar options
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
  eventContent: function(arg) {
    if (arg.event.extendedProps.staffCount) {
      const count = arg.event.extendedProps.staffCount;
      const total = arg.event.extendedProps.totalStaffs;
      const percentage = parseFloat(arg.event.extendedProps.percentage);
      
      // Create main container
      const container = document.createElement('div');
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      container.style.alignItems = 'center';
      container.style.padding = '2px';
      
      // Create dot container
      const dotContainer = document.createElement('div');
      dotContainer.style.display = 'flex';
      dotContainer.style.justifyContent = 'center';
      dotContainer.style.marginBottom = '2px';
      
      // Create the dot
      const dot = document.createElement('div');
      dot.style.width = '8px';
      dot.style.height = '8px';
      dot.style.borderRadius = '50%';
      
      // Set color based on percentage
      if (percentage === 50) {
        dot.style.backgroundColor = '#FFD700'; // Yellow
      } else if (percentage > 50) {
        dot.style.backgroundColor = '#00FF00'; // Green
      } else {
        dot.style.backgroundColor = '#FF0000'; // Red
      }
      
      dotContainer.appendChild(dot);
      
      // Create text container
      const textContainer = document.createElement('div');
      textContainer.style.textAlign = 'center';
      textContainer.style.fontSize = '0.8em';
      
      // Add count/total
      const countText = document.createElement('div');
      countText.textContent = `${count}/${total}`;
      
      // Add percentage
      const percentText = document.createElement('div');
      percentText.textContent = `${percentage}%`;
      
      textContainer.appendChild(countText);
      textContainer.appendChild(percentText);
      
      container.appendChild(dotContainer);
      container.appendChild(textContainer);
      
      return { domNodes: [container] };
    }
    return null;
  },
  eventClassNames: 'calendar-event',
  slotMinTime: '09:00:00', // Start time for time grid
  slotMaxTime: '19:00:00', // End time for time grid
  businessHours: {
    startTime: '09:00', // Start time for business hours
    endTime: '18:00', // End time for business hours
    daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
}}));

async function handleDateClick(info) {
  const clickedDate = new Date(info.dateStr);

  if (clickedDate < computeMinDate.value) {
    alert('You cannot select a date before two months ago.');
  } else if (clickedDate > computeMaxDate.value) {
    alert('You cannot select a date beyond three months ahead.');
  } else {
    console.log('Date clicked:', info.dateStr);
    selectedDate.value = info.dateStr;

    // Update the right container content
    const rightContentHtml = `
      <div class="right-container-header">
        <h2>Details for ${info.dateStr}</h2>
      </div>
    `;
    rightContent.value = rightContentHtml;
    isRightContainerVisible.value = true;
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
  height: 100%;
}

.calendar-container {
  width: 66.66%; 
  padding: 1rem;
}

.right-container {
  width: 33.33%;
  padding: 1rem;
  background-color: #f5f5f5;
  border-left: 1px solid #ddd;
}

.fc {
  width: 100%;
  height: 100%;
}

:deep(.calendar-event) {
  background: transparent!important;
  border: none!important;
}

:deep(.fc-event-main) {
  padding: 2px;
}

:deep(.fc-daygrid-event) {
  white-space: normal!important;
}

:deep(.fc-event-title) {
  color: #000000!important;
}

:deep(.fc-daygrid-event-harness) {
  margin-bottom: 2px!important;
}

:deep(.calendar-event *) {
  color: #000000!important;
}
</style>
