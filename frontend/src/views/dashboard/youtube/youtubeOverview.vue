<template>
  <link href="https://fonts.googleapis.com/css?family=Inter" rel="stylesheet" />
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-page-header>
          <template #content>
            <span class="title"> Youtube Analytics </span>
          </template>
          <div class="description">
            <br />
            Here’s whats happening in your Channel recently
            <br />
          </div>
          <template #extra>
            <div class="">
              <el-avatar
                class="profile"
                :size="32"
                src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              />
            </div>
          </template>
        </el-page-header>
      </el-header>
      <br /><br />
      <el-main>
        <el-menu
          class="el-menu-demo"
          default-active="/youtube/Overview"
          mode="horizontal"
          router="true"
          background-color="#F7F7FC"
          text-color="black"
          @select="handleSelect"
        >
          <el-menu-item index="/youtube/Overview">Overview</el-menu-item>
          <el-menu-item index="/youtube/Engagement">Engagement</el-menu-item>
          <el-menu-item index="/youtube/Reach">Reach</el-menu-item>
          <el-menu-item index="/youtube/AdCampaign">Ad Campaigns</el-menu-item>
        </el-menu>
      </el-main>
      <el-main>
        <BarChart :chart-options="chartOptions" :chart-data="chartData" />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { youtubeService } from '@/services/youtube';
import BarChart from '@/components/BarChart.vue';
export default {
  components: { BarChart },

  async mounted() {
    this.loaded = false;

    const { getDailySubscribers } = youtubeService();
    const today = new Date();
    var year = today.getFullYear();
    var month = String(today.getMonth() + 1).padStart(2, '0');
    var day = String(today.getDate()).padStart(2, '0');
    var dataLabels = [];
    var dataValues = [];
    var count = 0;
    try {
      while (count <= 30) {
        if (parseInt(day) == 0) {
          month = String(parseInt(month) - 1).padStart(2, '0');
          day = new Date(parseInt(year), parseInt(month), 0).getDate();
          if (parseInt(month) == 0) {
            year = String(parseInt(year) - 1);
            month = String(12).padStart(2, '0');
          }
        }
        var formattedDate = `${year}-${month}-08`;
        var subscribers = await getDailySubscribers(formattedDate);
        if (subscribers != null) {
          dataValues.push(subscribers);
          dataLabels.push(day + '/' + month);
        }
        day -= 1;
        count += 1;
      }
      this.chartData.datasets[0]['data'] = dataValues;
      this.chartData.labels = dataLabels;

      this.loaded = true;
    } catch (e) {
      console.error(e);
    }
  },
  data() {
    return {
      chartData: {
        labels: [],
        datasets: [{ data: [] }],
      },
      chartOptions: {
        responsive: true,
      },
    };
  },
};
</script>

<style>
body {
  background-color: #f7f7fc;
}
.profile {
  border-style: solid;
  border-color: black;
}
.title {
  font-size: large;
  font-family: 'Inter';
  font-weight: bold;
  font-size: large;
}
.description {
  text-align: left;
  font-family: 'Inter';
  color: #858688;
  font-size: smaller;
}
</style>
