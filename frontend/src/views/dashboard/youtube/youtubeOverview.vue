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
import { basicMetrics } from '@/helper/youtube';
import BarChart from '@/components/BarChart.vue';
export default {
  components: { BarChart },

  async mounted() {
    this.loaded = false;

    const { getSubscriberBarChart } = basicMetrics();
    try {
      var subscriberMetrics = await getSubscriberBarChart(60);
      this.chartData.labels = subscriberMetrics[0];
      this.chartData.datasets[0]['data'] = subscriberMetrics[1];
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
  methods: {
    basicMetrics,
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
