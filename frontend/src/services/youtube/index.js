import axios from 'axios';

const youtubeApi = 'https://localhost:8000/youtube/';

const youtubeService = () => {
  const getDayViews = async (date) => {
    const response = await axios.get(youtubeApi, 'day/', date, '/views');
    return response.data;
  };
  const getDayEngagement = async (date) => {
    const response = await axios.get(youtubeApi, 'day/', date, '/engagement');
    return response.data;
  };
  const getDayEstimatedMinsWatched = async (date) => {
    const response = await axios.get(
      youtubeApi,
      'day/',
      date,
      '/estimatedMinsWatched'
    );
    return response.data;
  };
  const getDayAverageViewDuration = async (date) => {
    const response = await axios.get(
      youtubeApi,
      'day/',
      date,
      '/averageViewDuration'
    );
    return response.data;
  };
  const getTotalViews = async () => {
    const response = await axios.get(youtubeApi, 'total/views');
    return response.data;
  };
  const getTotalLikes = async () => {
    const response = await axios.get(youtubeApi, 'total/likes');
    return response.data;
  };
  const getTotalDislikes = async () => {
    const response = await axios.get(youtubeApi, 'total/dislikes');
    return response.data;
  };
  const getTotalComments = async () => {
    const response = await axios.get(youtubeApi, 'total/comments');
    return response.data;
  };
  const getTotalShares = async () => {
    const response = await axios.get(youtubeApi, 'total/shares');
    return response.data;
  };
  const getTotalEngagement = async () => {
    const response = await axios.get(youtubeApi, 'total/engagement');
    return response.data;
  };
  const getTotalEstimatedMinutesWatched = async () => {
    const response = await axios.get(
      youtubeApi,
      'total/estimatedMinutesWatched'
    );
    return response.data;
  };
  const getTotalAverageViewDuration = async () => {
    const response = await axios.get(youtubeApi, 'total/averageViewDuration');
    return response.data;
  };

  return {
    getDayViews,
    getDayEngagement,
    getDayEstimatedMinsWatched,
    getDayAverageViewDuration,
    getTotalViews,
    getTotalLikes,
    getTotalDislikes,
    getTotalComments,
    getTotalShares,
    getTotalEngagement,
    getTotalEstimatedMinutesWatched,
    getTotalAverageViewDuration,
  };
};

export { youtubeService };
