import { ConfigService } from './index';

const GrafanaService = {
  /**
   * Builds an iframe-compatible Grafana dashboard panel URL.
   */
  async getDashboardEmbedUrl(
    uid: string,
    dashboardSlug: string,
    panelId: number,
    from?: number,
    to?: number
  ): Promise<string> {
    const config = new ConfigService().getConfig();

    if (!config?.grafanaURL) {
      throw new Error('Missing Grafana URL configuration.');
    }

    let url = `${config.grafanaURL}/d-solo/${uid}/${dashboardSlug}?shareView=public_dashboard&orgId=1&panelId=${panelId}`;

    if (from && to) {
      url += `&from=${from}&to=${to}`;
    }

    return url;
  },

  /**
   * Returns the Service Status dashboard embed URL (panelId 1).
   */
  async getServiceStatusDashboardEmbedUrl(
    uid: string,
    from?: number,
    to?: number
  ): Promise<string> {
    const dashboardSlug = 'ride-prod-status';
    const panelId = 1;

    return this.getDashboardEmbedUrl(uid, dashboardSlug, panelId, from, to);
  },

  /**
   * Returns the CPU Usage panel embed URL (panelId 6).
   */
  async getCpuUsagePanelUrl(from?: number, to?: number): Promise<string> {
    const uid = 'b5696b68-133a-404f-be64-1a53e3cba799'; //  dashboard UID
    const dashboardSlug = 'sysdig-dashboard';
  
    const panelId = 6;

    return this.getDashboardEmbedUrl(uid, dashboardSlug, panelId, from, to);
  },



  /**
   * Returns the Memory Usage panel embed URL (panelId 6).
   */

  async getMemoryUsagePanelUrl(from?: number, to?: number): Promise<string> {
    const uid = 'b5696b68-133a-404f-be64-1a53e3cba799'; //  dashboard UID
    const dashboardSlug = 'sysdig-dashboard';
  
    const panelId = 7;

    return this.getDashboardEmbedUrl(uid, dashboardSlug, panelId, from, to);
  },
  
  
    
  /**
   * Returns the Storage Usage panel embed URL (panelId 6).
   */
  async getStorageUsagePanelUrl(from?: number, to?: number): Promise<string> {
    const uid = 'b5696b68-133a-404f-be64-1a53e3cba799'; //  dashboard UID
    const dashboardSlug = 'sysdig-dashboard';
  
    const panelId = 11;

    return this.getDashboardEmbedUrl(uid, dashboardSlug, panelId, from, to);
  }
};

export default GrafanaService;
