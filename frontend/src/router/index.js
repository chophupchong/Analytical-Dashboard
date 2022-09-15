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
    component: () => import('@/views/dashboard/index.vue'),
  },
  {
    path: '/facebook',
    name: 'facebook',
    component: () => import('@/views/dashboard/facebook.vue'),
  },
  {
    path: '/instagram',
    name: 'instagram',
    component: () => import('@/views/dashboard/instagram.vue'),
  },
  {
    path: '/youTube',
    name: 'youTube',
    component: () => import('@/views/dashboard/youTube.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
