<template>
  <div>
    <canvas id="area-chart"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js'
import areaChartData from '../areadata.js'

export default {
  name: 'AreaChart',
  data() {
    return {
      areaChartData: areaChartData
    }
  },
  mounted() {
    const ctx = document.getElementById('area-chart');
    new Chart(ctx, this.areaChartData);
  }
}
</script>
