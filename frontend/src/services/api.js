import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyticsAPI = {
  askQuestion: async (storeId, question) => {
    try {
      const response = await api.post('/api/v1/questions', {
        store_id: storeId,
        question: question,
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error.response?.data || { error: 'Failed to connect to server' };
    }
  },
};

export default api;
