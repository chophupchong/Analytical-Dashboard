<template>
  <form action="#" @submit.prevent="Login" class="mt-4 flex flex-col">
    <h3 class="text-xl underline">Login</h3>

    <label for="email">Email:</label>
    <input
      class="border w-4/12"
      type="email"
      name="email"
      v-model="email"
      required
    />

    <label for="email">Password:</label>
    <input
      class="border w-4/12"
      type="password"
      name="password"
      v-model="password"
      required
    />

    <button
      class="w-max mt-4 px-4 py-2 text-center rounded-full bg-blue-500 text-white"
    >
      Login
    </button>
    <div v-if="error">{{ error }}</div>
  </form>
</template>

<script>
import { ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'login-view',
  setup() {
    const email = ref('');
    const password = ref('');
    const error = ref(null);

    const store = useStore();
    const router = useRouter();

    const Login = async () => {
      try {
        console.log(store.getters.authenticated);
        await store.dispatch('logIn', {
          email: email.value,
          password: password.value,
        });
        console.log(store.getters.authenticated);
        router.push('/');
      } catch (err) {
        error.value = err.message;
      }
    };
    return { Login, email, password, error };
  },
};
</script>
