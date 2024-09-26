import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import RequestView from '@/views/RequestView.vue'
import ApplicationView from '@/views/ApplicationView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      path: '/schedule',
      name: 'schedule',
      component: ScheduleView,
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
      component: ApplicationView
    }
    // ... other routes ...
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!localStorage.getItem('user')) {
      next('/login')
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})
