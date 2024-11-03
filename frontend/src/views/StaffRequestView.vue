<template>
    <div class="dashboard">
        <Navbar />

        <div class="row w-100 ms-0">
            <div class="col">
                <div class="card">
                    <div class="header">
                        <h2 class="h4 mb-0 fw-bold">My WFH Requests</h2>
                    </div>
                    <div class="filter-buttons d-flex justify-content-start align-items-center my-4 px-3">
                        <div class="toggle-container">
                            <div v-for="status in statuses" 
                                :key="status" 
                                @click="filterStatus = status" 
                                :class="['toggle-button', {'active': filterStatus === status}]">
                                    {{ status }}
                            </div>
                        </div>
                    </div>
                    <div v-if="isLoading" class="loading-overlay">
                        <div class="spinner"></div>
                    </div>
                    <div v-if="!isLoading" class="card-body shadow">
                        <div v-if="filteredRequests.length > 0" class="table">
                            <table class="table table-hover">
                                <thead class="thead-light">
                                    <tr>
                                        <th>Date Requested</th>
                                        <th>Start Date</th>
                                        <th>End Date</th>
                                        <th>Reason</th>
                                        <th>Request Type</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-for="request in filteredRequests" :key="request.request_id">
                                    <!-- Main Request Row -->
                                    <tr @click="toggleExpandRequest(request)">
                                        <td>{{ formatDate(request.request_date) }}</td>
                                        <td>{{ formatDate(request.start_date) }}</td>
                                        <td>{{ request.end_date ? formatDate(request.end_date) : '-' }}</td>
                                        <td>
                                            <span v-if="request.duration === 'WITHDRAWAL REQUEST' && request.status === 'REJECTED'">
                                                {{ request.reason_for_rejection }}
                                            </span>
                                            <span v-else>
                                                {{ request.reason_for_applying }}
                                            </span>
                                        </td>
                                        <td>
                                            <span v-if="request.is_recurring" class="badge bg-info ms-1">Recurring</span>
                                            <span v-else class="badge bg-primary ms-1">Ad-hoc</span>
                                            <span v-if="request.duration === 'WITHDRAWAL REQUEST'" class="badge bg-danger ms-1">Withdrawal</span>
                                            <span v-if="request.duration === 'FULL_DAY'" class="badge bg-success ms-1">Full Day</span>
                                            <span v-else-if="request.duration === 'HALF_DAY_AM'" class="badge bg-warning text-dark ms-1">AM</span>
                                            <span v-else-if="request.duration === 'HALF_DAY_PM'" class="badge bg-warning text-dark ms-1">PM</span>
                                        </td>
                                        <td>
                                            <span :class="getRequestStatus(request.status)">{{ request.status }}</span>
                                        </td>
                                        <td>
                                            <button v-if="request.status === 'PENDING' && request.duration!=='WITHDRAWAL REQUEST'" class="btn btn-danger btn-sm"
                                                @click.stop="cancelRequest(request.request_id)">
                                                Cancel
                                            </button>
                                            <button
                                                v-if="request.status === 'APPROVED' && !request.is_recurring && request.duration !== 'WITHDRAWAL REQUEST'"
                                                :class="{
                                                    'btn btn-warning btn-sm': isWithinWithdrawalPeriod(request.start_date) && request.withdrawn === false,
                                                    'btn btn-secondary btn-sm': !isWithinWithdrawalPeriod(request.start_date) || request.withdrawn === true
                                                }"
                                                @click.stop="openRejectForm(request)"
                                                :disabled="!isWithinWithdrawalPeriod(request.start_date) || request.withdrawn === true"
                                            >
                                                Withdraw
                                            </button>

                                        </td>
                                    </tr>
        
                                    <!-- Expanded Content Row -->
                                    <tr v-if="expandedRequestId === request.request_id && request.is_recurring">
                                    <td colspan="7" class="p-0">
                                        <div class="mx-3 my-2">
                                        <table class="table table-hover table-light">
                                            <thead class="thead-light">
                                                <tr>
                                                    <th>Schedule ID</th>
                                                    <th>Date</th>
                                                    <th>Request Type</th>
                                                    <th>Status</th>
                                                    <th>Action</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(schedule, index) in request.schedules" :key="index">
                                                    <td>{{ schedule.schedule_id }}</td>
                                                    <td>{{ formatDate(schedule.date) }}</td>
                                                    <td>
                                                        <span v-if="request.is_recurring" class="badge bg-info ms-1">Recurring</span>
                                                        <span v-if="request.duration === 'FULL_DAY'" class="badge bg-success ms-1">FULL DAY</span>
                                                        <span v-else-if="request.duration === 'HALF_DAY_AM'" class="badge bg-warning text-dark ms-1">AM</span>
                                                        <span v-else-if="request.duration === 'HALF_DAY_PM'" class="badge bg-warning text-dark ms-1">PM</span>
                                                    </td>
                                                    <td>
                                                        <span :class="getRequestStatus(schedule.status)">{{ schedule.status }}</span>
                                                    </td>
                                                    <td>
                                                        <button
                                                            v-if="schedule.status === 'APPROVED'"
                                                            :class="{
                                                                'btn btn-warning btn-sm': isWithinWithdrawalPeriod(schedule.date) && !schedule.withdrawn,
                                                                'btn btn-secondary btn-sm': !isWithinWithdrawalPeriod(schedule.date) || schedule.withdrawn
                                                            }"
                                                            @click.stop="openRejectForm(request, schedule)"
                                                            :disabled="!isWithinWithdrawalPeriod(schedule.date) || schedule.withdrawn"
                                                        >
                                                            Withdraw
                                                        </button>
                                                    </td>
                                                </tr>
                                            </tbody>
                                     </table>
                                </div>
                            </td>
                        </tr>
                    </template>
                </tbody>                  
                    </table>
                    <div v-if="showForm" class="form-overlay">
                        <div class="form-container">
                            <div class="form-header">
                                <h3 class="form-title">Withdraw WFH Request</h3>
                            </div>
                            <div class="table-wrapper">
                                <table class="table table-bordered" style="overflow:scroll;">
                                    <thead class="thead-light">
                                        <tr>
                                            <th>Date Requested</th>
                                            <th>Start Date</th>
                                            <th>End Date</th>
                                            <th>Reason</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>{{ formatDate(selectedRequest.request_date) }}</td>
                                            <td>{{ formatDate(selectedRequest.start_date) }}</td>
                                            <td>{{ selectedRequest.end_date ? formatDate(selectedRequest.end_date) : '-' }}</td>
                                            <td>{{ selectedRequest.reason_for_applying }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="form-group text-left px-5">
                                <label for="rej_reason" class="form-label">Reason for withdrawal:</label>
                                <textarea id="rej_reason" v-model="rej_reason" required class="form-control w-100" rows="3"></textarea>
                            </div>
                            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
                            <div class="form-actions">
                                <button type="button" @click="withdrawRequest" class="btn btn-danger">Withdraw</button>
                                <button type="button" @click="closeForm" class="btn btn-secondary">Cancel</button>
                            </div>
                        </div>
                    </div>
                </div>
                <p v-else class="text-muted">
                    No {{ filterStatus === 'All' ? '' : filterStatus }} requests found.
                </p>
            </div>
        </div>
    </div>
</div>

<!-- Cancel Confirmation Modal -->
<div v-if="showCancelConfirmation" class="form-overlay">
    <div class="form-container" style="width: 400px;">
        <div class="form-header">
            <h3 class="form-title">Confirm Cancellation</h3>
        </div>
        <div class="p-4">
            <p class="mb-4">Are you sure you want to cancel this WFH request?</p>
            <p class="text-muted small mb-4">This action cannot be undone.</p>
            <div class="form-actions">
                <button type="button" @click="confirmCancel" class="btn btn-danger">
                    Yes, Cancel Request
                </button>
                <button type="button" @click="closeCancelConfirmation" class="btn btn-secondary">
                    No, Keep Request
                </button>
            </div>
        </div>
    </div>
</div>
    </div>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { format, isValid } from 'date-fns'
import Navbar from '@/components/Navbar.vue'

const userData = ref({});
const allRequests = ref([]);
const isLoaded = ref(false);

const filterStatus = ref('All');;
// const statuses = ['All', 'Pending', 'Approved', 'Rejected', 'Expired', 'Cancelled', 'Withdrawn'];
const statuses = ['All', 'Pending', 'Approved', 'Rejected', 'Others'];
const showForm = ref(false);
const rej_reason = ref('');
const showCancelConfirmation = ref(false);
const requestToCancel = ref(null);
const expandedRequestId = ref(null);
const scheduleIds = ref([]);
const selectedRequest = ref([]);
const errorMessage = ref('');
const isLoading = ref(true);


// error here
const filteredRequests = computed(() => {
    if (filterStatus.value === 'All') {
        return allRequests.value;
    } else if (filterStatus.value === 'Others') {
        return allRequests.value.filter(request =>
            ['EXPIRED', 'CANCELLED', 'WITHDRAWN'].includes(request.status)
        );
    } else {
        return allRequests.value.filter(request => request.status === filterStatus.value.toUpperCase());
    }
});
const fetchRequests = async () => {
    try {
        const userData = JSON.parse(localStorage.getItem('user'));
        const response = await axios.get(
            `${import.meta.env.VITE_API_URL}/api/staff-requests/${userData.staff_id}`
        );

        const requests = response.data.staff_requests; // Get the requests
        const allRequestsArray = []; // Create an array to hold the combined requests and schedules

        // Loop through each request
        for (const request of requests) {
            // Format and add the request to the combined array
            allRequestsArray.push(request);

            // Fetch schedules for recurring requests
            if (request.is_recurring) {
                const scheduleResponse = await axios.get(
                    `${import.meta.env.VITE_API_URL}/api/schedules-by-ori-request-id/${request.request_id}`
                );
                console.log(scheduleResponse.data.schedules)
                if(scheduleResponse.data && scheduleResponse.data.schedules){
                    scheduleResponse.data.schedules.forEach(schedule => {
                    allRequestsArray.push(schedule);
                    });
                }
                }
                // Loop through the schedules and add them to the combined array

        }

        // Assign the combined requests and schedules to allRequests
        allRequests.value = allRequestsArray;
        console.log(allRequests.value)

    } catch (error) {
        console.error('Error fetching requests:', error);
        alert('Error fetching requests');
    } finally {
        isLoaded.value = true;
    }
};

// Cancel pending request
const cancelRequest = (request_id) => {
    requestToCancel.value = request_id;
    showCancelConfirmation.value = true;
};

// Handle the actual cancellation
const confirmCancel = async () => {
    try {
        const response = await axios.patch(`${import.meta.env.VITE_API_URL}/api/update-request`, {
            request_id: requestToCancel.value,
            request_status: 'CANCELLED',
            reason: ''
        });
        console.log('Cancellation response:', response.data);
        showCancelConfirmation.value = false;
        await fetchRequests();
    } catch (error) {
        console.error('Error cancelling request:', error);
        alert('Error cancelling request');
    }
};

// Close the confirmation modal
const closeCancelConfirmation = () => {
    showCancelConfirmation.value = false;
    requestToCancel.value = null;
};

const isWithinWithdrawalPeriod = (applicationDate) => {
    // console.log('request', applicationDate)
    const appDate = new Date(applicationDate);
    const today = new Date();

    const twoWeeksBefore = new Date(today);
    twoWeeksBefore.setDate(today.getDate() - 14);

    const twoWeeksAfter = new Date(today);
    twoWeeksAfter.setDate(today.getDate() + 14);

    return appDate >= twoWeeksBefore && appDate <= twoWeeksAfter;
};


// fetch schedules by request_id 
const fetchScheduleIds = async (request_id) => {
    try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/schedules-by-request-id/${request_id}`);

        if (response.data) {
            console.log('Fetched schedule IDs:', response.data.schedules);
            return response.data.schedules;
        } else {
            console.warn('No schedule IDs found for this request.');
            return [];
        }
    } catch (error) {
        console.error('Error fetching schedule IDs:', error);
        alert('Error fetching schedule IDs');
        return [];
    }
};
const toggleExpandRequest = async (request) => {
    if (expandedRequestId.value === request.request_id) {
        expandedRequestId.value = null;
        scheduleIds.value = [];
    } else {
        expandedRequestId.value = request.request_id;
        scheduleIds.value = await fetchScheduleIds(request.request_id);
    }
};

// check if request has been withdrawn before
const checkWithdrawalStatus = async (request_id, date) => {
    try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/check-withdrawal/${request_id}?schedule_date=${date}`)
        return response.data.withdrawn; // Return the withdrawal status
    } catch (error) {
        console.error('Error checking withdrawal status:', error);
        return false; 
    }
};

const checkAllWithdrawalStatuses = async () => {
    isLoading.value = true;
    try {
        for (const request of allRequests.value) {
            if (request.status === 'APPROVED') {
                if (request.is_recurring) {
                    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/schedules-by-request-id/${request.request_id}`);
                    const schedules = response.data.schedules;

                    for (const schedule of schedules) {
                        const formattedDate = formatScheduleDate(schedule.date);
                        schedule.withdrawn = await checkWithdrawalStatus(request.request_id, formattedDate);
                        schedule.status = request.status;
                    }
                    request.schedules = schedules;
                } else {
                    request.withdrawn = await checkWithdrawalStatus(request.request_id, request.start_date);
                }
            }
        }
    } finally {
        isLoading.value = false
    }
};


const withdrawRequest = async (request_id) => {
    if (!rej_reason.value.trim()) {
        errorMessage.value = 'Please provide a reason for rejection.';
        return;
    }

    console.log('Selected Request Data:', selectedRequest.value); // Log entire selected request
    console.log('Schedule ID being sent:', selectedRequest.value.schedule_id); // Log specific schedule_id
    console.log('Rejection Reason:', rej_reason.value); // Log rejection reason

    errorMessage.value = '';
    try {
        const schedule_id = selectedRequest.value.schedule_id;
        
        const requestData = {
            schedule_id: schedule_id,
            status: 'WITHDRAWN',
            reason: rej_reason.value
        };
        
        console.log('Data being sent to API:', requestData); // Log complete payload

        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/create-withdraw-request`, requestData);
        
        console.log('API Response:', response.data); // Log API response
        closeForm();
        await fetchRequests();
        await checkAllWithdrawalStatuses();
    } catch (error) {
        console.error('Error withdrawing request:', error);
        console.log('Error details:', error.response?.data); // Log error details if available
        alert('Error withdrawing request');
    }
};

const openRejectForm = async (request, schedule = null) => {
    console.log('Original Request:', request); // Log incoming request
    console.log('Schedule (if recurring):', schedule); // Log schedule if it exists
    
    try {
        if (schedule) {
            const modifiedRequest = {
                ...request,
                start_date: schedule.date,
                end_date: null,
                schedule_id: schedule.schedule_id
            };
            console.log('Modified Request (recurring):', modifiedRequest); // Log modified recurring request
            selectedRequest.value = modifiedRequest;
        } else {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/schedules-by-request-id/${request.request_id}`);
            console.log('API Response for schedule:', response.data.schedules); // Log API response
            
            const modifiedRequest = {
                ...request,
                schedule_id: response.data.schedules.map(schedule => schedule.schedule_id)[0]
            };
            console.log('Modified Request (non-recurring):', modifiedRequest); // Log modified non-recurring request
            selectedRequest.value = modifiedRequest;
        }
        
        showForm.value = true;
    } catch (error) {
        console.error('Error getting schedule data:', error);
        console.log('Error details:', error.response?.data); // Log error details if available
        alert('Error opening withdrawal form');
    }
};

const closeForm = () => {
  showForm.value = false;
  rej_reason.value = '';
  errorMessage.value = '';
  };


const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM d, yyyy');
}

const getRequestStatus = (requestStatus) => {
    switch (requestStatus) {
        default: return 'badge bg-secondary';
        case 'PENDING': return 'badge bg-warning';
        case 'APPROVED': return 'badge bg-success';
        case 'REJECTED': return 'badge bg-danger';
        case 'EXPIRED':
        case 'CANCELLED':
        case 'WITHDRAWN': return 'badge bg-secondary'
    }
}

const getStatusButtonClass = (requestStatus) => {
    switch (requestStatus) {
        case 'Pending':
            return filterStatus.value === requestStatus ? 'btn-warning' : 'btn-outline-warning';
        case 'Approved':
            return filterStatus.value === requestStatus ? 'btn-success' : 'btn-outline-success';
        case 'Rejected':
            return filterStatus.value === requestStatus ? 'btn-danger' : 'btn-outline-danger';
        case 'Others':
            return filterStatus.value === requestStatus ? 'btn-secondary' : 'btn-outline-secondary';
        default:
            return 'btn-outline-secondary';
    }
};

function formatScheduleDate(dateStr) {
    const date = new Date(dateStr);  // Parse the date string
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');  // getMonth is 0-based
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}
onMounted(async () => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        userData.value = JSON.parse(storedUser);
        await fetchRequests();
        await checkAllWithdrawalStatuses();
    
    }
});

</script>

<style scoped>
.active-filter {
    background-color: inherit;
    color: inherit;
    border-color: black;
}

.dashboard-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.dashboard-content {
    flex: 1;
    padding: 2rem 0;
}

.header {
    color: #141b4d;
    padding-top: 1rem;
}

.card {
    border: none;
    transition: box-shadow 0.3s ease-in-out;
}

.table {
    overflow-x: scroll;
}

.table th {
    font-weight: 600;
}

.table-wrapper {
    max-width: 100%;
    overflow-x: auto;
}

.badge {
    font-weight: 500;
}

.badge.bg-success {
    background-color: #28a745 !important;
}

.badge.bg-warning {
    background-color: #ffc107 !important;
}

.text-dark {
    color: #343a40 !important;
}

button {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    background-color: #1e2a6d
}

.btn-approve {
    background-color: green;
}

.btn-rej {
    background-color: red;
}

button:hover {
    color: black;
    /* font-weight: bold; */
}

.form-container {
    width: 70%;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    z-index: 100;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 0;
}

.form-header {
    width: 100%;
    background-color: #141b4d;
    padding: 1rem;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-bottom: 2rem;
}

.form-button {
    width: 30%;
    margin: 2rem;
}

#rej_reason {
    width: 100%;
    height: 40%;
}

.form-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.form-title {
    color: white;
    font-weight: bold;
}

.form-group {
    margin-bottom: 1.5rem;
    width: 100%;
}

.form-label {
    font-weight: 600;
    color: #141b4d;
    margin-bottom: 0.5rem;
    display: block;
    text-align: left;
}

.form-control {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
}

.error-message {
    color: #dc3545;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
}

.btn {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
}

.btn-warning {
    background-color: #ffc107;
}

.btn-success {
    background-color: #28a745;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-danger:hover {
    background-color: #c82333;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5a6268;
}
.form-container.small {
    width: 400px;
}

.form-actions .btn {
    width: auto;
    margin-bottom: 0;
}

.text-muted {
    color: #6c757d;
}

.small {
    font-size: 0.875rem;
}


.filter-buttons {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
    display: flex;
}

.toggle-container {
    display: flex;
    background-color: #f0f2f5;
    padding: 0.3rem;
    border-radius: 12px;
    gap: 0.3rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    min-width: fit-content; /* Ensures buttons don't shrink too much */
    flex-wrap: nowrap; /* Prevent wrapping */
    max-width: 100%; /* Ensure container doesn't overflow */
    margin: 0 auto; /* Center the container */
}

.toggle-button {
    padding: 0.5rem 1.2rem;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
    color: #666;
    user-select: none;
    white-space: nowrap;
    flex: 1; /* Allow buttons to grow equally */
    min-width: auto; /* Remove fixed min-width */
    text-align: center; /* Center text */
}

/* Update media queries for better responsive behavior */
@media screen and (max-width: 768px) {
    .toggle-container {
        padding: 0.25rem;
        gap: 0.25rem;
    }
    
    .toggle-button {
        padding: 0.4rem 0.8rem;
        font-size: 0.85rem;
    }
}

@media screen and (max-width: 480px) {
    .filter-buttons {
        padding: 0 0.5rem !important;
    }
    
    .toggle-container {
        padding: 0.2rem;
        gap: 0.2rem;
        width: 100%; /* Take full width on very small screens */
    }
    
    .toggle-button {
        padding: 0.35rem 0.6rem;
        font-size: 0.75rem;
    }
}

/* Add a new breakpoint for very small screens */
@media screen and (max-width: 360px) {
    .toggle-button {
        padding: 0.25rem 0.4rem;
        font-size: 0.7rem;
    }
}
.toggle-button:hover {
    background-color: rgba(255, 255, 255, 0.8);
    color: #333;
}

.toggle-button.active {
    background-color: white;
    color: #141b4d;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-button.active:has(:contains("Pending")) {
    color: #ffc107;
}

.toggle-button.active:has(:contains("Approved")) {
    color: #28a745;
}

.toggle-button.active:has(:contains("Rejected")) {
    color: #dc3545;
}

.toggle-button.active:has(:contains("Others")) {
    color: #6c757d;
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
  position: fixed;
  top: 50vh;        /* Changed to vh units */
  left: 50vw;       /* Changed to vw units */
  transform: translate(-50%, -50%);
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}
  
</style>
