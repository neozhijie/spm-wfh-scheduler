<template>
  <div id="app">
    <Navbar />
    <div class="dashboard-container">
      <div class="main-section">
        <div class="calendar-container">
          <FullCalendar 
            :options="calendarOptions"
          />
        </div>
        <div class="right-container" :class="{'show': isRightContainerVisible }">
          <div v-if="selectedDateDetails" class="details-container">
            <div class="details-header">
              <h2>Details for {{ selectedDate }}</h2>
              <!-- Close button is always rendered but hidden on larger screens via CSS -->
              <button class="close-button" @click="isRightContainerVisible = false">×</button>
            </div>
            <div class="time-slot" v-for="(slot, key) in selectedDateDetails" :key="key">
              <details open>
                <summary>
                  <span class="time-label">{{ key }}</span>
                  <div class="badge-container">
                    <span class="badge badge-office">
                      In Office ({{ slot.inOffice }}/{{ slot.total }})
                    </span>
                    <span class="badge badge-wfh">
                      WFH ({{ slot.wfh }}/{{ slot.total }})
                    </span>
                  </div>
                </summary>
                <div class="teams">
                  <div class="team card" v-for="team in slot.teams" :key="team.teamName">
                    <details>
                      <summary>
                        {{ team.teamName }}
                        <span class="badge badge-office">
                          In Office: {{ team.inOffice }}/{{ team.total }}
                        </span>
                        <span class="badge badge-wfh">
                          WFH: {{ team.wfh }}/{{ team.total }}
                        </span>
                      </summary>
                      <div class="staff-list">
                        <div class="staff-card" v-for="staff in team.staff" :key="staff.staff_id">
                          <span :class="['status-indicator', staff.status === 'OFFICE' ? 'green' : 'yellow']"></span>
                          <span class="staff-name">{{ staff.name }}</span>
                        </div>
                      </div>
                    </details>
                  </div>
                </div>
              </details>
            </div>
          </div>
          <div v-else class="no-selection">
            <p>Select a date on the calendar to view details.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import Navbar from '@/components/Navbar.vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import axios from 'axios';

const user = ref({});
const selectedDate = ref('');
const events = ref([]);
const selectedDateDetails = ref(null);
const isRightContainerVisible = ref(false);
const isSmallScreen = ref(window.innerWidth < 768); // Reactive property for screen size

const handleResize = () => {
  isSmallScreen.value = window.innerWidth < 768;
};

onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
    if (user.value.role === 3) {
      fetchManagerScheduleSummary(computeMinDate.value, computeMaxDate.value);
    }
  }
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

const computeMinDate = computed(() => {
  const date = new Date();
  date.setMonth(date.getMonth() - 2);
  date.setDate(date.getDate());
  return date;
});

const computeMaxDate = computed(() => {
  const date = new Date();
  date.setMonth(date.getMonth() + 3);
  return date;
});

function getColorForPercentage(percentage) {
  percentage = parseFloat(percentage);
  if (percentage < 50) {
    return '#FF6B6B'; // Red
  } else if (percentage < 75) {
    return '#FFD93D'; // Yellow
  } else {
    return '#6BCB77'; // Green
  }
}

async function fetchManagerScheduleSummary(start, end) {
  try {
    const startDateStr = start.toISOString().split('T')[0];
    const endDateStr = end.toISOString().split('T')[0];

    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/manager-schedule-summary/${user.value.staff_id}`, {
      params: {
        start_date: startDateStr,
        end_date: endDateStr
      }
    });

    const data = response.data.dates;
    const newEvents = [];

    data.forEach(item => {
      const dateStr = item.date;
      const totalStaff = item.total_staff;
      const officeCountAm = item.office_count_am;
      const officeCountPm = item.office_count_pm;

      const percentageAm = ((officeCountAm / totalStaff) * 100).toFixed(2);
      const percentagePm = ((officeCountPm / totalStaff) * 100).toFixed(2);

      const colorAm = getColorForPercentage(percentageAm);
      const colorPm = getColorForPercentage(percentagePm);

      newEvents.push({
        title: `(AM) In Office: ${officeCountAm} / ${totalStaff}`,
        start: dateStr + 'T09:00:00',
        end: dateStr + 'T13:00:00',
        allDay: false,
        extendedProps: {
          timeOfDay: 'AM',
          officeCount: officeCountAm,
          totalStaff,
          percentage: percentageAm
        },
        backgroundColor: colorAm,
        borderColor: colorAm
      });

      newEvents.push({
        title: `(PM) In Office: ${officeCountPm} / ${totalStaff}`,
        start: dateStr + 'T14:00:00',
        end: dateStr + 'T18:00:00',
        allDay: false,
        extendedProps: {
          timeOfDay: 'PM',
          officeCount: officeCountPm,
          totalStaff,
          percentage: percentagePm
        },
        backgroundColor: colorPm,
        borderColor: colorPm
      });
    });

    events.value = newEvents;
  } catch (error) {
    console.error('Error fetching manager schedule summary:', error);
  }
}

function getDateStr(dateObj) {
  // Ensure the date is formatted correctly using local timezone
  const year = dateObj.getFullYear();
  const month = ('0' + (dateObj.getMonth() + 1)).slice(-2);
  const day = ('0' + dateObj.getDate()).slice(-2);
  return `${year}-${month}-${day}`;
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
  eventClick: handleEventClick,
  datesSet: handleDatesSet,
  selectable: true,
  validRange: {
    start: computeMinDate.value,
    end: computeMaxDate.value,
  },
  weekends: false,
  events: events.value,
  allDaySlot: false,
  eventContent: function(arg) {
    if (arg.event.extendedProps.timeOfDay) {
      const timeOfDay = arg.event.extendedProps.timeOfDay;
      const officeCount = arg.event.extendedProps.officeCount;
      const totalStaff = arg.event.extendedProps.totalStaff;
      const percentage = arg.event.extendedProps.percentage;

      const container = document.createElement('div');
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      container.style.justifyContent = 'center';
      container.style.alignItems = 'flex-start'; // Align badges beside text
      container.style.backgroundColor = arg.event.backgroundColor;

      // Assign a class based on background color
      if (arg.event.backgroundColor === '#FFD93D') { // Yellow
        container.classList.add('yellow-event');
      } else {
        container.classList.add('default-event');
      }

      container.style.borderRadius = '4px';
      container.style.margin = '1px 0';
      container.style.padding = '2px 4px';
      container.style.fontSize = '0.8em';
      container.style.width = '100%';
      container.style.height = '100%';

      // Create a wrapper for the label and badges
      const labelContainer = document.createElement('div');
      labelContainer.style.display = 'flex';
      labelContainer.style.alignItems = 'center';
      labelContainer.style.width = '100%';
      labelContainer.style.justifyContent = 'space-between';

      const label = document.createElement('span');
      label.textContent = `${timeOfDay}`;

      const badgesWrapper = document.createElement('div');
      badgesWrapper.style.display = 'flex';
      badgesWrapper.style.gap = '4px';

      // Create Office Badge
      const officeBadge = document.createElement('span');
      officeBadge.classList.add('badge', 'badge-office-calendar');
      officeBadge.textContent = `In Office: ${officeCount}`;

      // Create WFH Badge
      const wfhBadge = document.createElement('span');
      wfhBadge.classList.add('badge', 'badge-wfh-calendar');
      wfhBadge.textContent = `WFH: ${totalStaff - officeCount}`;

      badgesWrapper.appendChild(officeBadge);
      badgesWrapper.appendChild(wfhBadge);

      labelContainer.appendChild(label);
      labelContainer.appendChild(badgesWrapper);

      container.appendChild(labelContainer);

      return { domNodes: [container] };
    }
    return null;
  },
  eventDidMount: function(info) {
    // This function is called after the event has been rendered

    // Ensure the container has the correct text color based on background
    const bgColor = info.event.backgroundColor.toUpperCase();
    const yellowHex = '#FFD93D';

    if (bgColor === yellowHex) {
      // Set text color to black
      info.el.style.color = '#000000';

      // Additionally, set all child elements to inherit the color
      // This ensures badges and other texts also become black
      const elements = info.el.querySelectorAll('*');
      elements.forEach(el => {
        // Override any inline styles that set color
        el.style.color = 'inherit';
      });
    } else {
      // Default text color (you can adjust this as needed)
      info.el.style.color = '#ffffff';

      const elements = info.el.querySelectorAll('*');
      elements.forEach(el => {
        el.style.color = 'inherit';
      });
    }
  },
  eventClassNames: 'calendar-event',
  slotMinTime: '09:00:00',
  slotMaxTime: '18:00:00',
  businessHours: {
    startTime: '09:00',
    endTime: '18:00',
    daysOfWeek: [1, 2, 3, 4, 5],
  },
}));

async function handleDateClick(info) {
  if (info.view.type === 'dayGridMonth') {
    const clickedDate = new Date(info.dateStr);

    if (clickedDate < computeMinDate.value + 1) {
      alert('You cannot select a date before two months ago.');
    } else if (clickedDate > computeMaxDate.value) {
      alert('You cannot select a date beyond three months ahead.');
    } else {
      selectedDate.value = info.dateStr;
      if (user.value.role === 3) {
        await displayDateDetails(info.dateStr);
      }
    }
  }
}

async function handleEventClick(info) {
  if (user.value.role === 3) {
    const dateStr = getDateStr(info.event.start);
    const viewType = info.view.type;
    if (viewType === 'timeGridWeek' || viewType === 'timeGridDay') {
      selectedDate.value = dateStr;
      await displayDateDetails(dateStr);
    }
  }
}

async function handleDatesSet(info) {
  if (info.view.type === 'timeGridDay') {
    const dateStr = getDateStr(info.start);
    selectedDate.value = dateStr;
    if (user.value.role === 3) {
      const detailData = await fetchManagerScheduleDetail(dateStr);
      if (detailData) {
        let groupedData = {
          AM: {
            inOffice: 0,
            wfh: 0,
            total: detailData.staff.length,
            teams: {}
          },
          PM: {
            inOffice: 0,
            wfh: 0,
            total: detailData.staff.length,
            teams: {}
          }
        };

        detailData.staff.forEach(staff => {
          const position = staff.position || 'Unknown';

          // AM
          if (!groupedData.AM.teams[position]) {
            groupedData.AM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
          }
          groupedData.AM.teams[position].total += 1;
          if (staff.status_am === 'OFFICE') {
            groupedData.AM.teams[position].inOffice += 1;
            groupedData.AM.inOffice += 1;
          } else {
            groupedData.AM.teams[position].wfh += 1;
            groupedData.AM.wfh += 1;
          }
          groupedData.AM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_am });

          // PM
          if (!groupedData.PM.teams[position]) {
            groupedData.PM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
          }
          groupedData.PM.teams[position].total += 1;
          if (staff.status_pm === 'OFFICE') {
            groupedData.PM.teams[position].inOffice += 1;
            groupedData.PM.inOffice += 1;
          } else {
            groupedData.PM.teams[position].wfh += 1;
            groupedData.PM.wfh += 1;
          }
          groupedData.PM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_pm });
        });

        groupedData.AM.total = detailData.staff.length;
        groupedData.PM.total = detailData.staff.length;

        selectedDateDetails.value = groupedData;
        // Only show the card on large screens when navigating dates
        if (!isSmallScreen.value) {
          isRightContainerVisible.value = true;
        }
        // On small screens, do not automatically show the card when navigating
      } else {
        alert('Error fetching details for the selected date.');
      }
    }
  }
}

async function displayDateDetails(dateStr) {
  const detailData = await fetchManagerScheduleDetail(dateStr);
  if (detailData) {
    let groupedData = {
      AM: {
        inOffice: 0,
        wfh: 0,
        total: detailData.staff.length,
        teams: {}
      },
      PM: {
        inOffice: 0,
        wfh: 0,
        total: detailData.staff.length,
        teams: {}
      }
    };

    detailData.staff.forEach(staff => {
      const position = staff.position || 'Unknown';

      // AM
      if (!groupedData.AM.teams[position]) {
        groupedData.AM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
      }
      groupedData.AM.teams[position].total += 1;
      if (staff.status_am === 'OFFICE') {
        groupedData.AM.teams[position].inOffice += 1;
        groupedData.AM.inOffice += 1;
      } else {
        groupedData.AM.teams[position].wfh += 1;
        groupedData.AM.wfh += 1;
      }
      groupedData.AM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_am });

      // PM
      if (!groupedData.PM.teams[position]) {
        groupedData.PM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
      }
      groupedData.PM.teams[position].total += 1;
      if (staff.status_pm === 'OFFICE') {
        groupedData.PM.teams[position].inOffice += 1;
        groupedData.PM.inOffice += 1;
      } else {
        groupedData.PM.teams[position].wfh += 1;
        groupedData.PM.wfh += 1;
      }
      groupedData.PM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_pm });
    });

    groupedData.AM.total = detailData.staff.length;
    groupedData.PM.total = detailData.staff.length;

    selectedDateDetails.value = groupedData;
    // Show the card
    isRightContainerVisible.value = true;
  } else {
    alert('Error fetching details for the selected date.');
  }
}

async function fetchManagerScheduleDetail(dateStr) {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/manager-schedule-detail/${user.value.staff_id}/${dateStr}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching manager schedule detail:', error);
    return null;
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.main-section {
  display: flex;
  height: 100%;
  overflow: hidden;
}

.calendar-container {
  width: 70%;
  padding: 1rem;
  flex: 1;
  min-width: 300px;
  overflow-y: auto;
}

.right-container {
  width: 30%;
  padding: 1rem;
  background-color: #ffffff;
  border-left: 1px solid #dfe3e8;
  overflow-y: auto;
  flex: none;
  min-width: 300px;
  height: 100%;
  position: relative;
}

.right-container.show {
  display: block;
}

.details-container {
  display: flex;
  flex-direction: column;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.details-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2e3a59;
}

/* Hide the close button on larger screens */
.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #888;
  display: none; /* Hidden by default */
}

/* Display the close button only on small screens */
@media (max-width: 768px) {
  .close-button {
    display: block;
  }
}

.time-slot {
  margin-bottom: 1em;
}

.time-label {
  font-weight: bold;
  margin-right: 0.5em;
}

.badge-container {
  display: flex;
  gap: 0.5em;
}

.badge {
  display: inline-block;
  padding: 0.25em 0.75em;
  border-radius: 12px;
  font-size: 0.85em;
  color: #ffffff; /* Default text color */
}

.badge-office {
  background-color: #6BCB77; /* Green */
}

.badge-wfh {
  background-color: #FFD93D; /* Yellow */
  color: #000000; /* Black text for better visibility */
}

.badge-office-calendar {
  background-color: #6BCB77; /* Green */
  color: #ffffff;
  font-size: 0.7em;
  padding: 2px 4px;
  border-radius: 8px;
}

.badge-wfh-calendar {
  background-color: #FFD93D; /* Yellow */
  color: #000000; /* Black text for better visibility */
  font-size: 0.7em;
  padding: 2px 4px;
  border-radius: 8px;
}

.teams {
  margin-left: 0.5em;
}

.team {
  margin-bottom: 0.5em;
  border: 1px solid #dfe3e8;
  border-radius: 8px;
  padding: 0.5em;
  background-color: #f9fafb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.team details summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  cursor: pointer;
  color: #2e3a59;
}

.team details[open] summary {
  border-bottom: 1px solid #dfe3e8;
  margin-bottom: 0.5em;
}

.team .badge {
  margin-left: 0.5em;
}

.staff-list {
  display: flex;
  flex-direction: column;
  margin-top: 0.5em;
}

.staff-card {
  display: flex;
  align-items: center;
  border: 1px solid #dfe3e8;
  border-radius: 6px;
  padding: 0.5em;
  margin-bottom: 0.5em;
  background-color: #ffffff;
}

.staff-card .status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 0.5em;
}

.staff-card .status-indicator.green {
  background-color: #6BCB77;
}

.staff-card .status-indicator.yellow {
  background-color: #FFD93D;
}

.staff-card .staff-name {
  font-weight: 500;
  color: #2e3a59;
}

.right-container details {
  margin: 0.5em 0;
}

.right-container summary {
  font-weight: bold;
  cursor: pointer;
  color: #2e3a59;
}

.fc {
  width: 100%;
  height: 100%;
}

.no-selection {
  text-align: center;
  color: #888;
  margin-top: 2rem;
}

.fc-event-main {
  padding: 2px;
}

.fc-daygrid-event {
  white-space: normal !important;
}

.calendar-event {
  /* Additional styling if needed */
}

.fc-daygrid-event-harness {
  margin-bottom: 2px !important;
}

/* Adjust the calendar height */
.fc .fc-view-harness {
  min-height: 0;
}

/* Hide the scrollbar but allow scrolling */
.calendar-container::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.right-container::-webkit-scrollbar {
  width: 8px;
}

.right-container::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.right-container::-webkit-scrollbar-track {
  background-color: transparent;
}

/* Media query for responsive layout */
@media (max-width: 768px) {
  .calendar-container {
    width: 100%;
  }

  .right-container {
    position: fixed; /* Change to fixed for overlay */
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background-color: rgba(255, 255, 255, 0.95); /* Semi-transparent background */
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out;
    z-index: 1000;
    overflow-y: auto;
    padding: 1rem;
  }

  .right-container.show {
    transform: translateX(0);
  }

  /* Ensure text within badges remains black on yellow backgrounds */
  .badge-wfh, .badge-wfh-calendar {
    color: #000000 !important;
  }
}

@media (max-width: 768px) {
  .main-section {
    flex-direction: column;
  }

  .right-container {
    width: 100%;
    min-width: unset;
    height: auto;
    position: fixed; /* Ensure it overlays */
    right: 0;
    top: 0;
    box-shadow: none;
    background-color: #ffffff;
  }

  .calendar-container {
    width: 100%;
    height: 100%;
  }

  .details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

/* New Styles for Conditional Text Colors */
.yellow-event {
  color: #000000 !important;
}

.default-event {
  color: #ffffff !important;
}

.yellow-event .badge,
.default-event .badge {
  color: inherit !important;
}
</style>