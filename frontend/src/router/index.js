import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

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
    path: '/youtube/Overview',
    name: 'youtubeOverview',
    component: () => import('@/views/dashboard/youtube/youtubeOverview.vue'),
  },
  {
    path: '/youtube/Engagement',
    name: 'youtubeEngagement',
    component: () => import('@/views/dashboard/youtube/youtubeEngagement.vue'),
  },
  {
    path: '/youtube/Reach',
    name: 'youtubeReach',
    component: () => import('@/views/dashboard/youtube/youtubeReach.vue'),
  },
  {
    path: '/youtube/AdCampaign',
    name: 'youtubeAdCampaign',
    component: () => import('@/views/dashboard/youtube/youtubeAdCampaign.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const access = await store.getters.authenticated;
  if (!access && to.name !== 'login') {
    router.push({ name: 'login' });
  } else {
    next();
  }
});

export default router;
