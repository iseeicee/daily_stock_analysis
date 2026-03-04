import apiClient from './index';
import { toCamelCase } from './utils';
import type {
  LogDetailResponse,
  LogsResponse,
} from '../types/logs';

// ============ API ============

export const logsApi = {
  /**
   * Get paginated backtest results
   */
  getResults: async (params: {
    code?: string;
    page?: number;
    limit?: number;
  } = {}): Promise<LogsResponse> => {
    const { code, page = 1, limit = 20 } = params;

    const queryParams: Record<string, string | number> = { page, limit };
    if (code) queryParams.code = code;

    const response = await apiClient.get<Record<string, unknown>>(
      '/api/v1/logs',
      { params: queryParams },
    );

    return toCamelCase<LogsResponse>(response.data);
  },

  /**
   * Get log detail
   */
  getLogDetail: async (fileName?: string, pointer?: number): Promise<LogDetailResponse | null> => {
    try {
      if (!fileName) return null;
      const queryParams = {
        pointer: pointer || 0,
      }
      const response = await apiClient.get<Record<string, unknown>>(
        '/api/v1/logs/' + fileName,
        { params: queryParams },
      );
      return toCamelCase<LogDetailResponse>(response.data);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number } };
        if (axiosErr.response?.status === 404) return null;
      }
      throw err;
    }
  },

};
