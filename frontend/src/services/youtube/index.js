import axios from 'axios';

const youtubeApi = 'http://localhost:8000/youtube/';

const youtubeService = () => {
  const postStoreBasicMetrics = async (months) => {
    const response = await axios.put(
      youtubeApi + 'store-Basic-Metrics/aggregated' + months
    );
    return response.data;
  };

  const getDailyViews = async (date) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/daily/' + date + '/views'
    );
    return response.data;
  };
  const getDailyEngagement = async (date) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/daily/' + date + '/engagement'
    );
    return response.data;
  };
  const getDailyEstimatedMinsWatched = async (date) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/daily/' + date + '/estimatedMinsWatched'
    );
    return response.data;
  };
  const getDailyAverageViewDuration = async (date) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/daily/' + date + '/averageViewDuration'
    );
    return response.data;
  };
  const getDailySubscribers = async (date) => {
    const response = await axios.get(
      youtubeApi + 'basic-metrics/daily/' + date + '/subscribers'
    );
    return response.data;
  };

  const getTotalViews = async () => {
    const response = await axios.get(youtubeApi + 'total/views');
    return response.data;
  };
  const getTotalLikes = async () => {
    const response = await axios.get(youtubeApi + 'total/likes');
    return response.data;
  };
  const getTotalDislikes = async () => {
    const response = await axios.get(youtubeApi + 'total/dislikes');
    return response.data;
  };
  const getTotalComments = async () => {
    const response = await axios.get(youtubeApi + 'total/comments');
    return response.data;
  };
  const getTotalShares = async () => {
    const response = await axios.get(youtubeApi + 'total/shares');
    return response.data;
  };
  const getTotalEngagement = async () => {
    const response = await axios.get(youtubeApi + 'total/engagement');
    return response.data;
  };
  const getTotalEstimatedMinutesWatched = async () => {
    const response = await axios.get(
      youtubeApi + 'total/estimatedMinutesWatched'
    );
    return response.data;
  };
  const getTotalAverageViewDuration = async () => {
    const response = await axios.get(youtubeApi + 'total/averageViewDuration');
    return response.data;
  };
  const getTotalSubscribers = async () => {
    const response = await axios.get(youtubeApi + 'total/subscribers');
    return response.data;
  };
  const getTotalSubscriberChange = async () => {
    const response = await axios.get(youtubeApi + 'total/subscriberChange');
    return response.data;
  };
  return {
    postStoreBasicMetrics,
    getDailyViews,
    getDailyEngagement,
    getDailyEstimatedMinsWatched,
    getDailyAverageViewDuration,
    getDailySubscribers,
    getTotalViews,
    getTotalLikes,
    getTotalDislikes,
    getTotalComments,
    getTotalShares,
    getTotalEngagement,
    getTotalEstimatedMinutesWatched,
    getTotalAverageViewDuration,
    getTotalSubscribers,
    getTotalSubscriberChange,
  };
};

export { youtubeService };
