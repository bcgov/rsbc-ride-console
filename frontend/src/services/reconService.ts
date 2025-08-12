import axios from 'axios';
import AuthService from './authService';

const ReconService = {
  async fetchEvents(type: string) {
    const accessToken = await new AuthService().getUserToken();
    return axios.get(`/api/${type}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      }
    });
  }
};

export default ReconService;
