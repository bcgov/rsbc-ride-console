// services/ErrorUpdateService.ts

import axios from 'axios';
import AuthService from './authService';

const withAuthHeaders = async () => {
  const accessToken = await new AuthService().getUserToken();
  return {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Cache-Control': 'no-cache',
      Pragma: 'no-cache',
    },
  };
};

const ErrorUpdateService = {
  setFixedById: async (objectId: string) => {
    const config = await withAuthHeaders();
    return axios.post('/api/errors/set-fixed', { object_id: objectId }, config);
  },

  setUnderAnalysisById: async (objectId: string) => {
    const config = await withAuthHeaders();
    return axios.post('/api/errors/set-under-analysis', { object_id: objectId }, config);
  },

  setAllFixed: async () => {
    const config = await withAuthHeaders();
    return axios.post('/api/errors/set-all-fixed', {}, config);
  },

  setAllUnderAnalysis: async () => {
    const config = await withAuthHeaders();
    return axios.post('/api/errors/set-all-under-analysis', {}, config);
  },
};

export default ErrorUpdateService;
