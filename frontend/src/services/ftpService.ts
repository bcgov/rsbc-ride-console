import axios from 'axios';
import type { AxiosRequestConfig, ResponseType } from 'axios';
import AuthService from './authService';

const withAuthHeaders = async (): Promise<AxiosRequestConfig> => {
  const accessToken = await new AuthService().getUserToken();

  // Explicitly set responseType with correct type
  const responseType: ResponseType = 'blob';

  return {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Cache-Control': 'no-cache',
      Pragma: 'no-cache',
    },
    responseType,
  };
};

const FtpFileService = {
  // Rename a file
  renameFile: async (
    type: 'recon_ftp' | 'recon_ftp_archives',
    oldFilename: string,
    newFilename: string
  ) => {
    const config = await withAuthHeaders();
    const baseUrl =
      type === 'recon_ftp'
        ? '/api/ftp/recon_ftp/rename'
        : '/api/ftp/recon_ftp_archives/rename';

    return axios.put(
      `${baseUrl}?old_filename=${encodeURIComponent(
        oldFilename
      )}&new_filename=${encodeURIComponent(newFilename)}`,
      undefined,
      config
    );
  },

  // Download a file
  downloadFile: async (type: 'recon_ftp' | 'recon_ftp_archives', filename: string) => {
    const config = await withAuthHeaders();
    const baseUrl =
      type === 'recon_ftp'
        ? '/api/ftp/recon_ftp/download'
        : '/api/ftp/recon_ftp_archives/download';

    return axios.get(`${baseUrl}?filename=${encodeURIComponent(filename)}`, config);
  },

  // Delete a file
  deleteFile: async (type: 'recon_ftp' | 'recon_ftp_archives', filename: string) => {
    const config = await withAuthHeaders();
    const baseUrl =
      type === 'recon_ftp'
        ? '/api/ftp/recon_ftp/delete'
        : '/api/ftp/recon_ftp_archives/delete';

    return axios.delete(`${baseUrl}?filename=${encodeURIComponent(filename)}`, config);
  },
};

export default FtpFileService;
