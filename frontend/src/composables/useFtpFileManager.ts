import FtpFileService from '@/services/ftpService';
import FetchRecordsService from '@/services/fetchRecordsService';
import { StorageKey } from '@/utils/constants';

const storageType = window.sessionStorage;

function getCacheKeys(type: 'recon_ftp' | 'recon_ftp_archives') {
  return {
    dataKey: `${StorageKey.EVENTS}_ftp_${type}`,
    countKey: `${StorageKey.EVENT_COUNT}_ftp_${type}`,
  };
}

async function invalidateAndRefresh(type: 'recon_ftp' | 'recon_ftp_archives') {
  const { dataKey, countKey } = getCacheKeys(type);

  storageType.removeItem(dataKey);
  storageType.removeItem(countKey);

  const response = await FetchRecordsService.fetchRecords('ftp', type);
  const countRes = await FetchRecordsService.fetchCount('ftp', type);

  storageType.setItem(dataKey, JSON.stringify(response.data || []));
  storageType.setItem(countKey, String(countRes.data.count ?? 0));
}

export function useFtpFileManager() {
  // Rename a file
  const renameFile = async (
    type: 'recon_ftp' | 'recon_ftp_archives',
    oldFilename: string,
    newFilename: string
  ) => {
    await FtpFileService.renameFile(type, oldFilename, newFilename);
    await invalidateAndRefresh(type);
  };

  // Delete a file
  const deleteFile = async (type: 'recon_ftp' | 'recon_ftp_archives', filename: string) => {
    await FtpFileService.deleteFile(type, filename);
    await invalidateAndRefresh(type);
  };

  // Download a file (returns Blob, actual download must be handled in component)
  const downloadFile = async (type: 'recon_ftp' | 'recon_ftp_archives', filename: string) => {
    const response = await FtpFileService.downloadFile(type, filename);
    return response.data as Blob;
  };

  return {
    renameFile,
    deleteFile,
    downloadFile,
  };
}
