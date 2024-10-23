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
        <div class="right-container" :class="{'show': isRightContainerVisible }">
          <div v-if="selectedDateDetails" class="details-container">
            <div class="details-header">
              <h2>Details for {{ selectedDate }}</h2>
              <!-- Close button is only rendered for small screens -->
              <button 
                v-if="isSmallScreen" 
                class="close-button" 
                @click="isRightContainerVisible = false"
              >
                ×
              </button>
            </div>
            <div class="tabs">
              <button 
                :class="['tab', activeTab === 'AM' ? 'active' : '']" 
                @click="activeTab = 'AM'"
              >
                AM
              </button>
              <button 
                :class="['tab', activeTab === 'PM' ? 'active' : '']" 
                @click="activeTab = 'PM'"
              >
                PM
              </button>
            </div>
            <div class="tab-content">
              <div v-if="activeTab === 'AM'">
                <div class="summary">
                  <div class="summary-item">
                    <span class="summary-label">In Office:</span>
                    <span class="summary-value">{{ selectedDateDetails.AM.inOffice }} / {{ selectedDateDetails.AM.total }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">WFH:</span>
                    <span class="summary-value">{{ selectedDateDetails.AM.wfh }} / {{ selectedDateDetails.AM.total }}</span>
                  </div>
                </div>
                <div class="teams">
                  <div 
                    class="team card" 
                    v-for="team in selectedDateDetails.AM.teams" 
                    :key="team.teamName"
                    @click="toggleTeam('AM', team.teamName)"
                  >
                    <div class="team-header">
                      <h3>{{ team.teamName }}</h3>
                      <div class="badge-container">
                        <span class="badge badge-office">
                          In Office: {{ team.inOffice }}/{{ team.total }}
                        </span>
                        <span class="badge badge-wfh">
                          WFH: {{ team.wfh }}/{{ team.total }}
                        </span>
                      </div>
                    </div>
                    <div class="staff-list" v-if="expandedTeams['AM-' + team.teamName]">
                      <div class="staff-card" v-for="staff in team.staff" :key="staff.staff_id">
                        <span :class="['status-indicator', staff.status === 'OFFICE' ? 'green' : 'yellow']"></span>
                        <span class="staff-name">{{ staff.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="activeTab === 'PM'">
                <div class="summary">
                  <div class="summary-item">
                    <span class="summary-label">In Office:</span>
                    <span class="summary-value">{{ selectedDateDetails.PM.inOffice }} / {{ selectedDateDetails.PM.total }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">WFH:</span>
                    <span class="summary-value">{{ selectedDateDetails.PM.wfh }} / {{ selectedDateDetails.PM.total }}</span>
                  </div>
                </div>
                <div class="teams">
                  <div 
                    class="team card" 
                    v-for="team in selectedDateDetails.PM.teams" 
                    :key="team.teamName"
                    @click="toggleTeam('PM', team.teamName)"
                  >
                    <div class="team-header">
                      <h3>{{ team.teamName }}</h3>
                      <div class="badge-container">
                        <span class="badge badge-office">
                          In Office: {{ team.inOffice }}/{{ team.total }}
                        </span>
                        <span class="badge badge-wfh">
                          WFH: {{ team.wfh }}/{{ team.total }}
                        </span>
                      </div>
                    </div>
                    <div class="staff-list" v-if="expandedTeams['PM-' + team.teamName]">
                      <div class="staff-card" v-for="staff in team.staff" :key="staff.staff_id">
                        <span :class="['status-indicator', staff.status === 'OFFICE' ? 'green' : 'yellow']"></span>
                        <span class="staff-name">{{ staff.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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
const isSmallScreen = ref(window.innerWidth < 768);
const isLoading = ref(false);
const activeTab = ref('AM');
const expandedTeams = ref({});

const handleResize = () => {
  isSmallScreen.value = window.innerWidth < 768;
};

onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user.value = JSON.parse(storedUser);
    if (user.value.role === 2) {
      initiateChunkedSummaryLoading();
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
  return date;
});

const computeMaxDate = computed(() => {
  const date = new Date();
  date.setMonth(date.getMonth() + 3);
  return date;
});

function getColorForPercentage(percentage) {
  percentage = parseFloat(percentage);
  if (percentage != 100) {
    return '#FFD93D'; // Yellow
  }   else {
    return '#6BCB77'; // Green
  }
}

async function fetchStaffScheduleSummary(start, end) {
  try {
    const startDateStr = start.toISOString().split('T')[0];
    const endDateStr = end.toISOString().split('T')[0];

    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/staff-schedule-summary/${user.value.reporting_manager}`, {
      params: {
        start_date: startDateStr,
        end_date: endDateStr,
        staff_id: user.value.staff_id
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

    events.value = [...events.value, ...newEvents];
  } catch (error) {
    console.error('Error fetching staff schedule summary:', error);
  }
}

function getDateStr(dateObj) {
  const year = dateObj.getFullYear();
  const month = ('0' + (dateObj.getMonth() + 1)).slice(-2);
  const day = ('0' + dateObj.getDate()).slice(-2);
  return `${year}-${month}-${day}`;
}

const calendarOptions = computed(() => {
  let smallScreen = isSmallScreen.value;

  return {
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
        container.style.alignItems = 'flex-start';
        container.style.backgroundColor = arg.event.backgroundColor;

        if (arg.event.backgroundColor === '#FFD93D') {
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

        const officeBadge = document.createElement('span');
        officeBadge.classList.add('badge', 'badge-office-calendar');
        officeBadge.textContent = `In Office: ${officeCount}`;

        badgesWrapper.appendChild(officeBadge);

        if (!smallScreen) {
          const wfhBadge = document.createElement('span');
          wfhBadge.classList.add('badge', 'badge-wfh-calendar');
          wfhBadge.textContent = `WFH: ${totalStaff - officeCount}`;
          badgesWrapper.appendChild(wfhBadge);
        }

        labelContainer.appendChild(label);
        labelContainer.appendChild(badgesWrapper);

        container.appendChild(labelContainer);

        return { domNodes: [container] };
      }
      return null;
    },
    eventDidMount: function(info) {
      const bgColor = info.event.backgroundColor.toUpperCase();
      const yellowHex = '#FFD93D';

      if (bgColor === yellowHex) {
        info.el.style.color = '#000000';

        const elements = info.el.querySelectorAll('*');
        elements.forEach(el => {
          el.style.color = 'inherit';
        });
      } else {
        info.el.style.color = '#ffffff';

        const elements = info.el.querySelectorAll('*');
        elements.forEach(el => {
          el.style.color = 'inherit';
        });
      }
    },
    eventClassNames: 'calendar-event',
    slotMinTime: '09:00:00',
    slotMaxTime: '19:00:00',
    businessHours: {
      startTime: '09:00',
      endTime: '19:00',
      daysOfWeek: [1, 2, 3, 4, 5],
    },
  };
});

async function handleDateClick(info) {
  if (info.view.type === 'dayGridMonth') {
    const clickedDate = new Date(info.dateStr);

    if (clickedDate < computeMinDate.value + 1) {
      alert('You cannot select a date before two months ago.');
    } else if (clickedDate > computeMaxDate.value) {
      alert('You cannot select a date beyond three months ahead.');
    } else {
      selectedDate.value = info.dateStr;
      activeTab.value = 'AM';
      if (user.value.role === 2) {
        await displayDateDetails(info.dateStr);
      }
    }
  }
}

async function handleEventClick(info) {
  if (user.value.role === 2) {
    const dateStr = getDateStr(info.event.start);
    const viewType = info.view.type;
    if (viewType === 'timeGridWeek' || viewType === 'timeGridDay') {
      selectedDate.value = dateStr;
      activeTab.value = 'AM';
      await displayDateDetails(dateStr);
    }
  }
}

async function handleDatesSet(info) {
  if (info.view.type === 'timeGridDay') {
    const dateStr = getDateStr(info.start);
    selectedDate.value = dateStr;
    activeTab.value = 'AM';
    if (user.value.role === 2) {
      const detailData = await fetchStaffScheduleDetail(dateStr);
      if (detailData) {
        let groupedData = {
          AM: {
            inOffice: 0,
            wfh: 0,
            total: detailData.staff.length - 1,
            teams: {}
          },
          PM: {
            inOffice: 0,
            wfh: 0,
            total: detailData.staff.length - 1,
            teams: {}
          }
        };

        detailData.staff.forEach(staff => {
          const position = staff.position || 'Unknown';

          // AM
          if (!groupedData.AM.teams[position]) {
            groupedData.AM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
          }
          if (staff.staff_id != user.value.staff_id){
            groupedData.AM.teams[position].total += 1;
            if (staff.status_am === 'OFFICE') {
              groupedData.AM.teams[position].inOffice += 1;
              groupedData.AM.inOffice += 1;
            } else {
              groupedData.AM.teams[position].wfh += 1;
              groupedData.AM.wfh += 1;
            }
            groupedData.AM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_am });
          }
          // PM
          if (!groupedData.PM.teams[position]) {
            groupedData.PM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
          }
          if (staff.staff_id != user.value.staff_id){
            groupedData.PM.teams[position].total += 1;
            if (staff.status_pm === 'OFFICE') {
              groupedData.PM.teams[position].inOffice += 1;
              groupedData.PM.inOffice += 1;
            } else {
              groupedData.PM.teams[position].wfh += 1;
              groupedData.PM.wfh += 1;
            }
            groupedData.PM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_pm });
            }
        });



        selectedDateDetails.value = groupedData;
        expandedTeams.value = {}; // Reset expanded teams

        if (!isSmallScreen.value) {
          isRightContainerVisible.value = true;
        }
      } else {
        alert('Error fetching details for the selected date.');
      }
    }
  }
}

async function displayDateDetails(dateStr) {
  const detailData = await fetchStaffScheduleDetail(dateStr);
  if (detailData) {
    let groupedData = {
      AM: {
        inOffice: 0,
        wfh: 0,
        total: detailData.staff.length - 1,
        teams: {}
      },
      PM: {
        inOffice: 0,
        wfh: 0,
        total: detailData.staff.length - 1,
        teams: {}
      }
    };

    detailData.staff.forEach(staff => {
      const position = staff.position || 'Unknown';

      // AM
      if (!groupedData.AM.teams[position]) {
        groupedData.AM.teams[position] = { teamName: position, inOffice: 0, wfh: 0, total: 0, staff: [] };
      }
      if (staff.staff_id != user.value.staff_id){
        groupedData.AM.teams[position].total += 1;
        if (staff.status_am === 'OFFICE') {
          groupedData.AM.teams[position].inOffice += 1;
          groupedData.AM.inOffice += 1;
        } else {
          groupedData.AM.teams[position].wfh += 1;
          groupedData.AM.wfh += 1;
        }
        groupedData.AM.teams[position].staff.push({ staff_id: staff.staff_id, name: staff.name, status: staff.status_am });
      }
      console.log(groupedData.AM.teams[position])

      if (staff.staff_id != user.value.staff_id){
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
      }
    });

    selectedDateDetails.value = groupedData;
    expandedTeams.value = {}; // Reset expanded teams

    isRightContainerVisible.value = true;
  } else {
    alert('Error fetching details for the selected date.');
  }
}

async function fetchStaffScheduleDetail(dateStr) {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/staff-schedule-detail/${user.value.staff_id}/${dateStr}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching staff schedule detail:', error);
    return null;
  }
}

async function initiateChunkedSummaryLoading() {
  isLoading.value = true;
  const today = new Date();

  const ranges = [];

  const currentMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  const currentMonthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  ranges.push({ start: new Date(currentMonthStart), end: new Date(currentMonthEnd) });

  for (let i = 1; i <= 2; i++) {
    const start = new Date(today.getFullYear(), today.getMonth() - i, 1);
    const end = new Date(today.getFullYear(), today.getMonth() - i + 1, 0);
    ranges.push({ start, end });
  }

  for (let i = 1; i <= 3; i++) {
    const start = new Date(today.getFullYear(), today.getMonth() + i, 1);
    const end = new Date(today.getFullYear(), today.getMonth() + i + 1, 0);
    ranges.push({ start, end });
  }

  for (let i = 0; i < ranges.length; i++) {
    if (i === 0) {
      await fetchStaffScheduleSummary(ranges[i].start, ranges[i].end);
    } else {
      setTimeout(async () => {
        await fetchStaffScheduleSummary(ranges[i].start, ranges[i].end);
      }, i * 1000);
    }
  }
  isLoading.value = false;
}

function toggleTeam(timeOfDay, teamName) {
  const key = `${timeOfDay}-${teamName}`;
  expandedTeams.value[key] = !expandedTeams.value[key];
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
  position: relative;
}

.right-container {
  width: 30%;
  padding: 1.5rem;
  background-color: #f4f6f8;
  border-left: 1px solid #dfe3e8;
  overflow-y: auto;
  flex: none;
  min-width: 300px;
  height: 100%;
  position: relative;
  transition: transform 0.3s ease-in-out;
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
  margin-bottom: 1.5rem;
}

.details-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #2e3a59;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: #888;
}

.tabs {
  display: flex;
  margin-bottom: 1rem;
}

.tab {
  flex: 1;
  padding: 0.75rem 1rem;
  background-color: #e0e7ff;
  border: none;
  cursor: pointer;
  font-weight: 600;
  color: #141b4d;
  transition: background-color 0.3s ease;
}

.tab:not(:last-child) {
  border-right: 1px solid #c7d2fe;
}

.tab.active {
  background-color: #141b4d;
  color: #ffffff;
}

.tab:hover {
  background-color: #c7d2fe;
}

.tab-content {
  flex: 1;
}

.summary {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.summary-item {
  display: flex;
  align-items: center;
}

.summary-label {
  font-weight: 600;
  margin-right: 0.5rem;
  color: #2e3a59;
}

.summary-value {
  font-weight: 500;
  color: #141b4d;
}

.teams {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.team {
  background-color: #ffffff;
  border: 1px solid #dfe3e8;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.team-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #2e3a59;
}

.badge-container {
  display: flex;
  gap: 0.5rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85em;
  color: #ffffff;
}

.badge-office {
  background-color: #6BCB77; /* Green */
}

.badge-wfh {
  background-color: #FFD93D; /* Yellow */
  color: #000000; /* Black text for better visibility */
}

.staff-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.staff-card {
  display: flex;
  align-items: center;
  border: 1px solid #dfe3e8;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  background-color: #f9fafb;
}

.status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 0.75rem;
}

.status-indicator.green {
  background-color: #6BCB77;
}

.status-indicator.yellow {
  background-color: #FFD93D;
}

.staff-name {
  font-weight: 500;
  color: #2e3a59;
  font-size: 0.8rem;

}

.no-selection {
  text-align: center;
  color: #888;
  margin-top: 2rem;
  font-size: 1.1rem;
}

.fc {
  width: 100%;
  height: 100%;
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
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background-color: rgba(255, 255, 255, 0.95);
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out;
    z-index: 1000;
    overflow-y: auto;
    padding: 1.5rem;
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
    position: fixed;
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

  .tabs {
    flex-direction: row;
    justify-content: space-between;
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

/* Loading Overlay Styles */
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
  border: 8px solid #f3f3f3; /* Light grey */
  border-top: 8px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Indicate that team cards are clickable */
.team.card {
  transition: background-color 0.2s ease;
}

.team.card:hover {
  background-color: #f0f4ff;
}
</style>
