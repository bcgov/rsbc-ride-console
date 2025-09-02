// services/ProducerService.ts
import axios from 'axios';
import AuthService from './authService';

const withAuthHeaders = async () => {
  const accessToken = await new AuthService().getUserToken();
  return {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Cache-Control': 'no-cache',
      Pragma: 'no-cache',
      'Content-Type': 'application/json',
    },
  };
};

const ProducerService = {
  send: async (apipath: string, payload: Record<string, any>) => {
    const config = await withAuthHeaders();
    return axios.post(
      '/api/producer/send', 
      {
        apipath,
        payload,
      },
      config
    );
  },
};

export default ProducerService;
