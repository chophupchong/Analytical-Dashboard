import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login'),
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/dashboard'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
