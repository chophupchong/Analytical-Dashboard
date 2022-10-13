import { youtubeService } from '@/services/youtube';

const { getDailyBasicMetrics, getAggregatedBasicMetrics } = youtubeService();

const basicMetrics = () => {
  const getSubscriberBarChart = async (days) => {
    var dataLabels = [];
    var dataValues = [];
    try {
      var basicMetrics = await getDailyBasicMetrics(days);
      basicMetrics = basicMetrics['Chop Hup Chong'];

      for (const date of Object.keys(basicMetrics)) {
        dataLabels.push(date);
        dataValues.push(basicMetrics[date]['subscribers']);
      }
    } catch (e) {
      console.error(e);
    }
    return [dataLabels, dataValues];
  };

  const getAggregatedBasicMetricData = async (days) => {
    try {
      var aggregatedBasicMetrics = await getAggregatedBasicMetrics(days);
      aggregatedBasicMetrics = aggregatedBasicMetrics['Chop Hup Chong'];

      var metrics = aggregatedBasicMetrics;
    } catch (e) {
      console.error(e);
    }
    return metrics;
  };

  const getPercentageChange = async (days) => {
    try {
      var aggregatedBasicMetrics = await getAggregatedBasicMetrics(days);
      aggregatedBasicMetrics = aggregatedBasicMetrics['Chop Hup Chong'];

      var percentageChangeMetrics =
        aggregatedBasicMetrics['metricsPercentageChange'];
    } catch (e) {
      console.error(e);
    }
    return percentageChangeMetrics;
  };

  return {
    getSubscriberBarChart,
    getAggregatedBasicMetricData,
    getPercentageChange,
  };
};

export { basicMetrics };
