interface ImportMetaEnv {
  readonly VITE_GRAFANA_URL: string;
  readonly VITE_GRAFANA_TOKEN: string;
  readonly VITE_API_RIDE_KEY_PRODUCER: string;
  readonly VITE_PRODUCER_API_URL: string;
 
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
