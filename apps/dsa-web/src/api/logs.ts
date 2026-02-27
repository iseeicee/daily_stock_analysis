import apiClient from './index';
import { toCamelCase } from './utils';
import type {
  BacktestRunRequest,
  LogDetail, LogDetailResponse,
  LogsResponse,
  PerformanceMetrics,
} from '../types/logs';

// ============ API ============

export const logsApi = {
  /**
   * Trigger backtest evaluation
   */
  run: async (params: BacktestRunRequest = {}): Promise<LogDetail> => {
    const requestData: Record<string, unknown> = {};
    if (params.code) requestData.code = params.code;
    if (params.force) requestData.force = params.force;
    if (params.fileName) requestData.eval_window_days = params.fileName;
    if (params.minAgeDays != null) requestData.min_age_days = params.minAgeDays;
    if (params.limit) requestData.limit = params.limit;

    const response = await apiClient.post<Record<string, unknown>>(
      '/api/v1/backtest/run',
      requestData,
    );
    return toCamelCase<LogDetail>(response.data);
  },

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
   * Get overall performance metrics
   */
  getLogDetail: async (fileName?: string): Promise<LogDetailResponse | null> => {
    try {
      if (!fileName) return null;
      const response = await apiClient.get<Record<string, unknown>>(
        '/api/v1/logs/' + fileName.fileName,
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
