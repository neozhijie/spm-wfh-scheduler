import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import RequestView from '@/views/RequestView.vue'
import ApplicationView from '@/views/ApplicationView.vue'
import ManagerScheduleView from '@/views/ManagerTeamScheduleView.vue'
import TeamScheduleView from '@/views/StaffTeamScheduleView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/schedule',
      name: 'schedule',
      component: ScheduleView,
      meta: { requiresAuth: true }
    },
    {
      path: '/teamschedule-manager',
      name: 'managerschedule',
      component: ManagerScheduleView,
      meta: { requiresAuth: true }
    },
    {
      path: '/teamschedule-staff',
      name: 'teamschedule',
      component: TeamScheduleView,
      meta: { requiresAuth: true }
    },
    {
      path: '/requests',
      name: 'requests',
      component: RequestView,
      meta: { requiresAuth: true }
    },
    {
      path: '/application',
      name: 'application',
      component: ApplicationView,
      meta: {requiresAuth: true}
    },
    // ... other routes ...
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!localStorage.getItem('user')) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router