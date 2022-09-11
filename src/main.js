import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import { firestorePlugin } from 'vuefire';
// Import the functions you need from the SDKs you need

createApp(App).use(firestorePlugin).use(router).use(store).mount('#app');
