import axios from 'axios';

// const youtubeApi = 'http://localhost:8000/youtube/';
const youtubeApi = 'https://chc-api.onrender.com/youtube/';

const youtubeService = () => {
  const storeAggregatedBasicMetricsByDay = async (months) => {
    const response = await axios.put(
      youtubeApi + 'store-basic-metrics/aggregated/' + months
    );
    return response.data;
  };

  const storeDailyBasicMetrics = async (months) => {
    const response = await axios.put(
      youtubeApi + 'store-Basic-Metrics/aggregated/' + months
    );
    return response.data;
  };

  const storeTotalBasicMetrics = async (months) => {
    const response = await axios.put(
      youtubeApi + 'store-Basic-Metrics/total/' + months
    );
    return response.data;
  };

  const getDailyBasicMetrics = async (days) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/daily/' + days
    );
    return response.data;
  };

  const getAggregatedBasicMetrics = async (days) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/aggregated/' + days
    );
    return response.data;
  };

  return {
    storeAggregatedBasicMetricsByDay,
    storeDailyBasicMetrics,
    storeTotalBasicMetrics,
    getDailyBasicMetrics,
    getAggregatedBasicMetrics,
  };
};

export { youtubeService };
