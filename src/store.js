import { createStore } from 'vuex';

const store = createStore({
  state: {
    user: {
      loggedIn: false,
      data: null,
    },
  },
});

// export the store
export default store;
