<template>
    <div class="dashboard">
        <Navbar />

        <div class="row w-100 ms-0">
            <div class="col">
                <div class="card">
                    <div class="header">
                        <h2 class="h4 mb-0 fw-bold">My WFH Requests</h2>
                    </div>
                <div class="filter-buttons d-flex justify-content-start align-items-center my-3">
                    <div v-for="status in statuses" :key="status" class="me-2">
                        <button 
                            @click="filterStatus = status" 
                            :class="['btn',getStatusButtonClass(status)]">
                            {{ status }}
                        </button>
                    </div>
                </div>
                    <div v-if="isLoaded" class="card-body shadow">
                        <div v-if="filteredRequests.length>0" class="table">
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
                                    <tr v-for="request in filteredRequests" :key="request.request_id">
                                        <td>{{ formatDate(request.request_date) }}</td>
                                        <td>{{ formatDate(request.start_date) }}</td>
                                        <td>{{ request.end_date ? formatDate(request.end_date) : '-' }}</td>
                                        <td>{{ request.reason_for_applying }}</td>
                                        <td>
                                            <span v-if="request.is_recurring" class="badge bg-info ms-1">Recurring</span>
                                            <span v-else class="badge bg-primary ms-1">Ad-hoc</span>
                                            <span v-if="request.duration === 'FULL_DAY'" class="badge bg-success ms-1">FULL DAY</span>
                                            <span v-else-if="request.duration === 'HALF_DAY_AM'" class="badge bg-warning text-dark ms-1">AM</span>
                                            <span v-else-if="request.duration === 'HALF_DAY_PM'" class="badge bg-warning text-dark ms-1">PM</span>
                                        </td>
                                        <td>
                                            <span :class="getRequestStatus(request.status)">{{ request.status }}</span>
                                        </td>
                                        <td>
                                            <!-- <button v-if="request.status === 'PENDING'" 
                                                    class="btn btn-danger btn-sm" 
                                                    @click="cancelRequest(request.request_id)">
                                                Cancel
                                            </button> -->
                                            <button v-if="request.status === 'APPROVED'" 
                                                    class="btn btn-warning btn-sm" 
                                                    @click="withdrawRequest(request.request_id)">
                                                Withdraw
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>

                            </table>
                        </div>
                    <p v-else class="text-muted">
                        No {{ filterStatus === 'All' ? '' : filterStatus }} requests found.
                    </p>
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

        // console.log('userData:', userData);
        // console.log('response:', response);
        // console.log('requests:', response.data);
        // console.log(typeof (response.data));
        // console.log('err');

        allRequests.value = response.data.staff_requests;
        // console.log('allRequests:', allRequests.value);

    } catch (error) {
        console.error('Error fetching requests:', error);
        alert('Error fetching requests');
    } finally {
        isLoaded.value = true;
    }
}

// const cancelRequest = async (request_id) => {
//     try {
//         const response = await axios.patch(`${import.meta.env.VITE_API_URL}/api/update-request`, {
//             request_id: request_id,
//             request_status: 'CANCELLED',
//         });
//         console.log('Cancellation response:', response.data);
//         await fetchRequests();
//     } catch (error) {
//         console.error('Error cancelling request:', error);
//         if (error.response && error.response.data && error.response.data.message) {
//             alert(`Error cancelling request: ${error.response.data.message}`);
//         } else {
//             alert('Error cancelling request');
//         }
//     }
// };

const withdrawRequest = async (request_id) => {
    try {
        const response = await axios.patch(`${import.meta.env.VITE_API_URL}/api/update-request`, {
            request_id: request_id,
            request_status: 'WITHDRAWN',
            reason: ''
        });
        console.log('Withdrawal response:', response.data);
        await fetchRequests();
    } catch (error) {
        console.error('Error withdrawing request:', error);
        alert('Error withdrawing request');
    }
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

onMounted(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        userData.value = JSON.parse(storedUser);
        fetchRequests();
    }
})

const selectedRequest = ref(null);
const errorMessage = ref('');

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
    padding-top: 4rem;
    padding-bottom: 2rem;
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
</style>
