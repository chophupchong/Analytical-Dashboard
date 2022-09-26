<template>
  <link href='https://fonts.googleapis.com/css?family=Inter' rel='stylesheet'>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-page-header >
          <template #content>
            <span class="title"> Youtube Analytics </span>
          </template>
          <div class="description">
            <br>
            Here’s whats happening in your Channel recently
            <br>
          </div>
          <template #extra>
            <div class="">
              <el-avatar
               class="profile" :size="32" 
                src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"/>
            </div>
    </template>
        </el-page-header>
      </el-header>
      <br><br>
      <el-main>
        <el-menu
          class="el-menu"
          router = "true"
          default-active="/youtube/Engagement"
          mode="horizontal"
          background-color="#F7F7FC"
          text-color="black"
          @select="handleSelect"
        >
          <el-menu-item class ="el-menu-item" index="/youtube/Overview">Overview</el-menu-item>
          <el-menu-item class ="el-menu-item" index="/youtube/Engagement">Engagement</el-menu-item>
          <el-menu-item class ="el-menu-item" index="/youtube/Reach">Reach</el-menu-item>
          <el-menu-item class ="el-menu-item" index="/youtube/AdCampaign">Ad Campaigns</el-menu-item>
        </el-menu>
      </el-main>
    </el-container>
  </div>
</template>

<script>

export default {};




</script>

<style>
body {
  background-color: #F7F7FC;
}
.el-menu {   
  
  text-decoration: none;
}
.profile {
  border-style: solid;
  border-color: black;
}
.title {
  font-size:large;
  font-family: 'Inter';
  font-weight: bold;
  font-size:large
}
.description {
  text-align: left;
  font-family: 'Inter';
  color:#858688;
  font-size:smaller;
}


</style>