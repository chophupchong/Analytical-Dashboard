<template>
  <AreaChart/>
</template>

<script>
import AreaChart from "../charts/AreaChart.vue";

export default {
    name: "App",
    components: {
        AreaChart,
    },
    data() {
    return {
      chartData: {
        Books: 24,
        Magazine: 30,
        Newspapers: 10
      }
    };
  }

}
</script>

<style>

</style>