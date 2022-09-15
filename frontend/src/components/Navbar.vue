<template>

  <div id="nav">
    <h2>Analytics</h2>
    <!-- for all users -->
    <router-link class="routerlink" to="/">Overview</router-link>
    <router-link class="routerlink" to="/">Facebook</router-link>
    <router-link class="routerlink" to="/youtube">Youtube</router-link>
    <router-link class="routerlink" to="/">Instagram</router-link>

    <div id="container">
    <router-link class="routerlink" to="/login">Settings</router-link>
    <router-link class="routerlink" to="/login">Logout</router-link>
    </div>
    <!-- for logged in users -->
  </div>
</template>

<script>
export default {
  name: 'navbar-component',
};
</script>

<style scoped>

h2{
  color: white;
}
#container {
  display: flex;
  flex-direction: column;
  margin-top: 5px;
  border-top:solid;
  border-color: #31313d;
}
#nav {
  display: flex;
  flex-direction: column;
  background-color: #1B1C1E;
  justify-content: flex-start;
  align-items: center;
  height: 100vh;
  width: 12%;
  top: 0;
  overflow: auto;
  position: fixed;
  font-family: "Poppins", sans-serif;
  font-weight: 300;
  color: white;
  font-size: 16px;
}
  

.routerlink {   
  display: block;
  text-decoration: none;
  padding: 10px;
  margin: 2px;
  font-weight: 600;
  text-align:left;
  transition-property: color, background;
  transition-duration: 0.3s;
  text-decoration: none;
}

  
.routerlink:hover {
  border-radius: 5px;
  background: #323335;
  min-width: 100px;
}
  
.routerlink:visited {
  border-radius: 5px;
  min-width: 100px;
  color: #62666b;
}
  
.routerlink:link {
  border-radius: 5px;
  min-width: 100px;
  color: #323335;
}
</style>
