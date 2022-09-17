<template>
  <el-container>
    <el-aside width="200px"> <navbar-2 /></el-aside>
    <el-main><router-view /></el-main>
  </el-container>
</template>
<script>
// import Navbar from "./components/Navbar.vue";
import Navbar2 from "./components/Navbar2.vue";
// import Navbar2 from "./components/Navbar2.vue";
export default {
  components: { Navbar2 },
};
</script>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

body {
  margin: 0;
}
nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}

::-webkit-scrollbar {
  width: 10px;
}

/* Track */
::-webkit-scrollbar-track {
  background: #f1f1f1;
}

/* Handle */
::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 15px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.el-aside {
  min-height: 100vh;
}
</style>
