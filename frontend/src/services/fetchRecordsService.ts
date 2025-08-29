import axios from 'axios';
import AuthService from './authService';

type RecordType = 'reconciliation' | 'error' | 'ftp';

const prefixMap: Record<RecordType, string> = {
  reconciliation: 'recon',
  error: 'errors',
  ftp: 'ftp'
};


const FetchRecordsService = {
  async fetchRecords(type: RecordType, category: string) {
    const accessToken = await new AuthService().getUserToken();
    const prefix = prefixMap[type];
    const url = `/api/${prefix}/${category}`;
    
    
    return axios.get(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      }
    });
  },

  async fetchCount(type: RecordType, category: string) {
    const accessToken = await new AuthService().getUserToken();
    const prefix = prefixMap[type];
    const url = `/api/${prefix}/${category}/count`;

    return axios.get(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      }
    });
  }
};

export default FetchRecordsService;
