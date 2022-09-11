<template>
  <div class="mt-4">
    <div v-for="blog in blogs" :key="blog.id">
      <div class="mt-4 mb-4">
        <h3 class="text-xl underline">{{ blog.title }}</h3>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Pariatur
          aspernatur consectetur doloremque sunt ducimus enim iure animi fugit
          nulla et! Perferendis autem deleniti quo eum corrupti reiciendis
          voluptatem ab ducimus?
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
export default {
  name: 'dashboard-view',
  setup() {
    const blogs = ref([
      { title: 'What is programming?', id: 1 },
      { title: 'What is JS?', id: 2 },
      { title: 'What is Python?', id: 3 },
    ]);
    return {
      blogs,
    };
  },
};
</script>
