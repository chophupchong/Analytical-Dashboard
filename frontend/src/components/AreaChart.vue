<template>
  <div>
    <canvas id="area-chart"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js'
import planetChartData from '../areadata.js'

export default {
  name: 'AreaChart',
  data() {
    return {
      planetChartData: planetChartData
    }
  },
  mounted() {
    const ctx = document.getElementById('planet-chart');
    new Chart(ctx, this.planetChartData);
  }
}
</script>
