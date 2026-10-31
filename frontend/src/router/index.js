import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/socios',
  },
  {
    path: '/socios',
    name: 'socios',
    component: () => import('@/views/SociosView.vue'),
  },
  {
    path: '/enrolamiento',
    name: 'enrolamiento',
    component: () => import('@/views/EnrolamientoView.vue'),
  },
  {
    path: '/reconocimiento',
    name: 'reconocimiento',
    component: () => import('@/views/ReconocimientoView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
