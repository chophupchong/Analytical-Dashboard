import axios from 'axios';

const youtubeApi = 'http://localhost:8000/youtube/';

const youtubeService = () => {
  const postStoreBasicMetrics = async (months) => {
    const response = await axios.put(
      youtubeApi + 'store-Basic-Metrics/aggregated/' + months
    );
    return response.data;
  };

  const getBasicMetrics = async (days) => {
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
    postStoreBasicMetrics,
    getBasicMetrics,
    getAggregatedBasicMetrics
  };
};

export { youtubeService };
