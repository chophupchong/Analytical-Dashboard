import { youtubeService } from '@/services/youtube';

const { getBasicMetrics } = youtubeService();

const basicMetrics = () => {
  const getSubscriberBarChart = async (days) => {
    var dataLabels = [];
    var dataValues = [];
    try {
      var basicMetrics = await getBasicMetrics(days);
      for (const date of Object.keys(basicMetrics)) {
        dataLabels.push(date);
        dataValues.push(basicMetrics[date]['subscribers']);
      }
    } catch (e) {
      console.error(e);
    }
    return [dataLabels, dataValues];
  };

  return {
    getSubscriberBarChart,
  };
};

export { basicMetrics };
