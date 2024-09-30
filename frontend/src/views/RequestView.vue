<template>
  <div class="dashboard">
    <Navbar />

    <div class="row w-100 ms-0">
      <div class="col">
        <div class="card">
          <div class="header">
            <h2 class="h4 mb-0 fw-bold">Pending WFH Requests</h2>
          </div>
          <div v-if="isLoaded" class="card-body shadow">
            <div v-if="pendingRequests.length > 0" class="table">
              <table class="table table-hover">
                <thead class="thead-light">
                  <tr>
                    <th>Date Requested</th>
                    <th>Name</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Reason</th>
                    <th>Request Type</th>
                    <th>Approve/Reject</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in pendingRequests" :key="request.request_id">
                    <td>{{ formatDate(request.request_date) }}</td>
                    <td>{{ staffNames[request.staff_id] || 'Loading...' }}</td>
                    <td>{{ formatDate(request.start_date) }}</td>
                    <td>{{ request.end_date ? formatDate(request.end_date) : '-' }}</td>
                    <td>{{ request.reason_for_applying }}</td>
                    <td>
                      <span v-if="request.is_recurring" class="badge bg-info ms-1">Recurring</span>
                      <span v-else="request.is_recurring" class="badge bg-primary ms-1"
                        >Ad-hoc</span
                      >
                    </td>
                    <td>
                      <span><button class="btn-approve" >Approve</button></span>
                      <span><button class="btn-rej" @click = "openRejectForm(request)">Reject</button></span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if = "showForm" class = "form-container">
                <form>
                  <table class="table">
                    <thead class="thead-light">
                      <tr>
                        <th>Date Requested</th>
                        <th>Name</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                        <th>Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>{{ formatDate(selectedRequest.request_date) }}</td>
                        <td>{{ staffNames[selectedRequest.staff_id] || 'Loading...' }}</td>
                        <td>{{ formatDate(selectedRequest.start_date) }}</td>
                        <td>{{ selectedRequest.end_date ? formatDate(selectedRequest.end_date) : '-' }}</td>
                        <td>{{ selectedRequest.reason_for_applying }}</td>
                      </tr>
                    </tbody>
                  </table>
                  <label for="rej_reason">Reason for rejection:</label>
                  <p><input type="text" id="rej_reason" v-model="rej_reason"></p>
                  <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>

                  <button type="button" @click="submitRejection" class = "form-button">Submit</button>
                  <button type="button" @click="closeForm" class = "form-button">Cancel</button>
                </form>
              </div>
            </div>
            <p v-else class="text-muted">No pending requests.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { format, isValid } from 'date-fns'
import Navbar from '@/components/Navbar.vue'

const user = ref({})
const userData = JSON.parse(localStorage.getItem('user'))
const pendingRequests = ref([])
const isLoaded = ref(false)

const fetchPendingRequests = async () => {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/pending-requests/${userData.staff_id}`
    )
    pendingRequests.value = response.data

    // Fetch names for all staff IDs
    for (const request of pendingRequests.value) {
      if (!staffNames.value[request.staff_id]) {
        getNameById(request.staff_id)
      }
    }
  } catch (error) {
    console.error('Error fetching pending requests:', error)
    alert('Error fetching pending requests')
  }
}

const formatDate = (dateString) => {
  return format(new Date(dateString), 'MMM d, yyyy')
}

const staffNames = ref({})
const getNameById = async (staffId) => {
  if (staffNames.value[staffId]) {
    return staffNames.value[staffId]
  }
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/staff/${staffId}`)
    const name = `${response.data.staff_fname} ${response.data.staff_lname}`
    staffNames.value[staffId] = name
    isLoaded.value = true
    return name
  } catch (error) {
    console.error('Error fetching staff name:', error)
    alert('Error fetching staff name')
    return 'Unknown'
  }
}
onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    user.value = JSON.parse(storedUser)
    fetchPendingRequests()
  }
})

const showForm = ref(false);
const rej_reason = ref('');
const selectedRequest = ref(null);
const errorMessage = ref('');

const openRejectForm = (request) => {
  // Log the request to inspect the data passed
  console.log('Request data:', request);

  // Check if the request object and date fields are defined
  if (!request || !request.request_date || !request.start_date) {
    console.error('Invalid request data:', request);

    return;
  }

  // Assign the selected request and open the form
  selectedRequest.value = request;
  showForm.value = true;
};

const closeForm = () => {
  showForm.value = false;
  };

const submitRejection = () => {
  if (!rej_reason.value.trim()) {
    errorMessage.value = 'Please provide a reason for rejection.';
    return;  // Prevent submission
  }

  // Clear the error message if there is valid input
  errorMessage.value = '';

  console.log(`Rejection reason for ${selectedRequest.value.request_id}: ${rej_reason.value}`);
  closeForm();
  };

</script>

<style scoped>
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

.badge {
  font-weight: 500;
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
  font-weight: bold;
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
}

.form-button {
  width: 30%;
  margin: 2rem;
}

#rej_reason {
  width: 80%;
  height: 40%;
}
</style>
