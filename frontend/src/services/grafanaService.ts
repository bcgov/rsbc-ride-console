import axios from 'axios';
import { ConfigService } from './index';

const GrafanaService = {
  
  /**
   * Returns a full dashboard embed URL suitable for iframes.
   * 
   */
  async getDashboardEmbedUrl(uid: string, from?: number, to?: number): Promise<string> {
    
    const config = new ConfigService().getConfig();

    if (!config?.grafanaURL) {
      throw new Error('Missing Grafana URL configuration.');
    }
    const grafanaUrl = config.grafanaURL;



    try {
     

      let url = `${grafanaUrl}/d-solo/${uid}/ride-prod-status?shareView=public_dashboard&orgId=1&panelId=1`;

      if (from && to) {
        url += `&from=${from}&to=${to}`;
      }

      return url;
    } catch (error) {
      console.error('Error generating dashboard iframe URL:', error);
      throw error;
    }
  }
};

export default GrafanaService;
