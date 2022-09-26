<template>
  <el-row class="tac" id="nav">
    <el-col :span="24">
      <div id="nav-title">
        <el-icon id="title-icon" :size="25" color="#ffffff"
          ><Histogram
        /></el-icon>
        <h3 class="mb-2" id="nav-title-text">Analytics</h3>
      </div>
      <el-menu
        router="true"
        default-active="/"
        class="el-menu-vertical-demo"
        @open="handleOpen"
        @close="handleClose"
        background-color="#1A1B1D"
        active-text-color="#FFFFFF"
        text-color="#5B5C5E"
        unique-opened="true"
      >
        <el-sub-menu index="1">
          <template #title>
            <el-icon><location /></el-icon>
            <span class="profile-name">Chop Hup Chong</span>
          </template>
          <el-menu-item index="/">Overview</el-menu-item>
          <el-menu-item index="/facebook">Facebook</el-menu-item>
          <el-menu-item index="/instagram">Instagram</el-menu-item>
          <el-menu-item index="/youtube/Overview">Youtube</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="2">
          <template #title>
            <el-icon><location /></el-icon>
            <span class="profile-name">Food Yo</span>
          </template>
          <el-menu-item index="2-1">Overview</el-menu-item>
          <el-menu-item index="2-2">Facebook</el-menu-item>
          <el-menu-item index="2-3">Instagram</el-menu-item>
          <el-menu-item index="2-4">Youtube</el-menu-item>
        </el-sub-menu>
        <el-divider class="nav-divider" />
        <el-menu-item index="2-4">Profile Management</el-menu-item>
        <el-divider class="nav-divider" />
        <el-menu-item index="2-4"
          ><el-icon id="title-icon" :size="20" color="#5B5C5E"
            ><Tools /></el-icon
          >Settings</el-menu-item
        >
        <el-menu-item index="2-4">Logout</el-menu-item>
      </el-menu>
    </el-col>
  </el-row>
</template>

<script setup>
/*use script setup to locally register component by simply importing the component*/
import { Histogram, Tools } from "@element-plus/icons-vue";
</script>

<script>
export default {
  name: "navbar-component",
};
</script>

<style scoped>
#nav {
  min-height: 100vh;
  background-color: #1a1b1d;
}
#nav-title-text {
  /* padding-top: 30px; */
  /* padding-bottom: 20px; */
  margin: 0;
  color: #fff;
  background-color: #1a1b1d;
  margin-top: 5px;
}

.profile-name {
  color: #858587;
}
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  /* min-height: 100vh; */
  border-right-width: 0px;
}
#nav-title {
  display: flex;
  flex-direction: row;
  justify-content: center;
  margin-top: 30px;
  margin-bottom: 20px;
  align-items: center;
}

#title-icon {
  margin-right: 5px;
}

.nav-divider {
  margin-top: 0px;
  margin-bottom: 0px;
  margin-right: 10px;
  padding-right: 0px;
  width: 180px;
  margin-left: 10px;
  border-top-color: #22222b;
  border-top-width: 3px;
}
</style>