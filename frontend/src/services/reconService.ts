import axios from 'axios';
import AuthService from './authService';

const ReconService = {
  async fetchEvents(type: string) {
    const accessToken = await new AuthService().getUserToken();

    const response = await axios.get(`/api/${type}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      }
    });

    return response;
  },

  async fetchCount(type: string) {
    const accessToken = await new AuthService().getUserToken();

    const response = await axios.get(`/api/${type}/count`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      }
    });

    return response;
  }
};

export default ReconService;
