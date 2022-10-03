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
      <el-row >
        <el-col :span="11">
          <el-row >
            <el-col :span="11" :offset="1">
      
              <el-card>
                <el-row>
                  <el-icon class="logo" :size="32" color="#5B5C5E"><Tools /></el-icon> 
                  <div class="metricNames">Subscribers</div>
                </el-row>
                <el-row>
                  <el-col :span="6">
                    <span class="metricNumber">{{aggregatedBasicMetricData['subscribers']}}</span>
                  </el-col>
                  
                  <el-col :span="6" :offset="6">
                      <span class="logo" v-if="aggregatedPercentageChangeData['subscribersPercentChange'] > 0"> + {{aggregatedPercentageChangeData['subscribersPercentChange']}} %</span>
                      <span class="logo" v-else-if="aggregatedPercentageChangeData['subscribersPercentChange'] < 0"> - {{aggregatedPercentageChangeData['subscribersPercentChange']}} %</span>
                      <span class="logo" v-else> No change</span>
                      <div class="percentDisplay" v-if="last30days == true">This month</div>
                  </el-col>
                </el-row>
              </el-card>
            </el-col>
    
            <el-col :span="11" :offset="1">
              <el-card>
                <el-row>
                  <el-icon class="logo" :size="32" color="#5B5C5E"><Tools /></el-icon> 
                  <div class="metricNames">Engagement</div>
                </el-row>
                <el-row>
                  <el-col :span="6">
                    <span class="metricNumber">{{aggregatedBasicMetricData['engagement']}}</span>
                  </el-col>
          
                  <el-col :span="6" :offset="6">
                      <span class="logo" v-if="aggregatedPercentageChangeData['engagementPercentChange'] > 0"> + {{aggregatedPercentageChangeData['engagementPercentChange']}} %</span>
                      <span class="logo" v-else-if="aggregatedPercentageChangeData['engagementPercentChange'] < 0"> - {{aggregatedPercentageChangeData['engagementPercentChange']}} %</span>
                      <span class="logo" v-else> No change</span>
                      <div class="percentDisplay" v-if="last30days == true">This month</div>
                  </el-col>
                </el-row>
              </el-card>
            </el-col>
          </el-row>
      <el-row >
   
  </el-row>

  <BarChart :chart-options="chartOptions" :chart-data="chartData" />
</el-col>
</el-row>
    </el-container>
  </div>
</template>

<script setup>
  /*use script setup to locally register component by simply importing the component*/
  import { Tools } from '@element-plus/icons-vue';

</script>

<script>
import { basicMetrics } from '@/helper/youtube';
import BarChart from '@/components/BarChart.vue';
export default {
  components: { BarChart },

  async mounted() {
    this.loaded = false;

    const { getSubscriberBarChart, getAggregatedBasicMetricData , getPercentageChange} = basicMetrics();
    try {
      var AggregatedBasicMetric = await getAggregatedBasicMetricData(30);
      var aggregatedPercentageChange = await getPercentageChange(30);

      var subscriberMetrics = await getSubscriberBarChart(60);
      this.chartData.labels = subscriberMetrics[0];
      this.chartData.datasets[0]['data'] = subscriberMetrics[1];

      this.aggregatedBasicMetricData = AggregatedBasicMetric;
      this.aggregatedPercentageChangeData = aggregatedPercentageChange;

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
      aggregatedBasicMetricData: 0,
      aggregatedPercentageChangeData: {},
      last30days: true
    };
  },
  methods: {
    basicMetrics,
  },
};
</script>

<style>
.logo {
  margin-right: 5px;
  font-size:medium;
  white-space: nowrap ;
}
.metricNumber { 
  margin-right: 5px;
  font-size:large;
  white-space: nowrap ;

}
.el-row {
  margin-bottom: 8px;
  
}
.percentDisplay {
  white-space: nowrap ;
  padding-top: 10px;
}
.metricNames {
  margin-top: 6px;
  margin-left:5px;
  font-size: large;
  font-family: 'Inter';
  font-weight: bold;
  font-size: large;
}

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
