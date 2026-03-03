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

    const data = toCamelCase<LogsResponse>(response.data);
    return {
      total: data.total,
      page: data.page,
      limit: data.limit,
      items: (data.items || []),
    };
  },

  /**
   * Get log detail
   */
  getLogDetail: async (fileName?: string): Promise<LogDetailResponse | null> => {
    try {
      if (!fileName) return null;
      const response = await apiClient.get<Record<string, unknown>>(
        '/api/v1/logs/' + fileName,
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
