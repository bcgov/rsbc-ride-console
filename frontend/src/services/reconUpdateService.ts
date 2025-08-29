// services/ReconUpdateService.ts

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

const ReconUpdateService = {

  resetAllByType: async (type: string) => {
    const config = await withAuthHeaders();
    return axios.post(`/api/recon/${type}/reset-all`, {}, config);
  },

  // Unified: Reset a specific event by type and ID
  resetById: async (type: string, objectId: string) => {
    const config = await withAuthHeaders();
    return axios.post(`/api/recon/${type}/reset`, { object_id: objectId }, config);
  },


   deleteEventById: async (type: string, objectId: string) => {
    const config = await withAuthHeaders();
    return axios.delete(`/api/recon/${type}/${objectId}`, config);
  },

   deleteAllEvents: async (type: string) => {
    const config = await withAuthHeaders();
    return axios.delete(`/api/recon/${type}`, config);
  },
  
};

export default ReconUpdateService;
