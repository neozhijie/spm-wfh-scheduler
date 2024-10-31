import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
import { createApp } from 'vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import App from './App.vue'
import router from './router'

library.add(faSignOutAlt)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)

app.mount('#app')
