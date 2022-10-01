import { signInWithEmailAndPassword, signOut } from 'firebase/auth';
import { createStore } from 'vuex';
import { auth } from './firebase';

const store = createStore({
  state: {
    user: {
      loggedIn: false,
    },
  },
  getters: {
    authenticated(state) {
      return state.user.loggedIn;
    },
  },
  mutations: {
    SET_LOGGED_IN(state) {
      state.user.loggedIn = true;
    },
    SET_LOGGED_OUT(state) {
      state.user.loggedIn = false;
    },
  },
  actions: {
    async logIn(context, { email, password }) {
      const response = await signInWithEmailAndPassword(auth, email, password);
      if (response) {
        context.commit('SET_LOGGED_IN');
      } else {
        throw new Error('Login Failed');
      }
    },
    async logOut(context) {
      await signOut(auth);
      context.commit('SET_LOGGED_OUT');
    },
  },
});

export default store;
