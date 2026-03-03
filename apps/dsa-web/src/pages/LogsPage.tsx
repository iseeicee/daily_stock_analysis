
import type React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { logsApi } from '../api/logs';
import { Pagination } from '../components/common';
import type {
  LogInfo,
  LogDetailResponse,
} from '../types/logs';


// ============ Main Page ============

const LogsPage: React.FC = () => {
  // Input state
  const [isRunning, setIsRunning] = useState(false);
  const [logDetail, setLogDetailResult] = useState<LogDetailResponse | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  // Results state
  const [results, setResults] = useState<LogInfo[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoadingResults, setIsLoadingResults] = useState(false);
  const pageSize = 20;

  // Fetch results
  const fetchResults = useCallback(async (page = 1, code?: string) => {
    setIsLoadingResults(true);
    try {
      const response = await logsApi.getResults({ code: code || undefined, page, limit: pageSize });
      setResults(response.items);
      setTotalResults(response.total);
      setCurrentPage(response.page);
    } catch (err) {
      console.error('Failed to fetch backtest results:', err);
    } finally {
      setIsLoadingResults(false);
    }
  }, []);

  // Initial load — fetch performance first, then filter results by its window
  useEffect(() => {
    const init = async () => {
      fetchResults(1, undefined);
    };
    init();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Search
  const getLogDetail = async (fileName: string) => {
    try {
      fileName = fileName.trim();
      const response = await logsApi.getLogDetail(fileName);
      setLogDetailResult(response?response:null);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : 'Fetch log detail failed');
    } finally {
      setIsRunning(false);
    }
  };

  // Pagination
  const totalPages = Math.ceil(totalResults / pageSize);
  const handlePageChange = (page: number) => {
    fetchResults(page);
  };

  // ============ Log Detail ============
  const LogDetail: React.FC<{ data: LogDetailResponse }> = ({ data }) => (
    <div className="flex items-center gap-4 px-3 py-2 rounded-lg bg-elevated border border-white/5 text-xs font-mono animate-fade-in">
      <span className="text-secondary">FileName: <span className="text-white">{data.fileName}</span></span>
      <span className="text-secondary">Pages: <span className="text-cyan">{data.pages}</span></span>
      <span className="text-secondary">Pointer: <span className="text-cyan">{data.pointer}</span></span>
      <span className="log-content">{data.content.map((line, index) => (
          <p className="text-white">{line}</p>
      ))}
      </span>
      {data.errors > 0 && (
        <span className="text-secondary">Errors: <span className="text-red-400">{data.errors}</span></span>
      )}
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col">

      {/* Main content */}
      <main className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Left sidebar - Performance */}
        <div className="flex flex-col gap-3 w-64 shrink-0 overflow-y-auto">
{isLoadingResults ? (
            <div className="flex flex-col items-center justify-center h-64">
              <div className="w-10 h-10 border-3 border-cyan/20 border-t-cyan rounded-full animate-spin" />
              <p className="mt-3 text-secondary text-sm">Loading results...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-12 h-12 mb-3 rounded-xl bg-elevated flex items-center justify-center">
                <svg className="w-6 h-6 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-base font-medium text-white mb-1.5">No Results</h3>
              <p className="text-xs text-muted max-w-xs">
                Run a backtest to evaluate historical analysis accuracy
              </p>
            </div>
          ) : (
            <div className="animate-fade-in">
              <div className="overflow-x-auto rounded-xl border border-white/5">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-elevated text-left">
                      {/* <th className="px-3 py-2.5 text-xs font-medium text-secondary uppercase tracking-wider">FileDate</th> */}
                      <th className="px-3 py-2.5 text-xs font-medium text-secondary uppercase tracking-wider">FileName</th>
                      <th className="px-3 py-2.5 text-xs font-medium text-secondary uppercase tracking-wider">FileSize</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((item, index) => (
                      <tr
                        key={item.fileName}
                        className="border-t border-white/5 hover:bg-hover transition-colors"
                      >
                        {/* <td className="px-3 py-2 font-mono text-cyan text-xs">{item.createdAt}</td> */}
                        <td className="px-3 py-2" onClick={() => getLogDetail(item.fileName)}>{item.fileName}</td>
                        <td className="px-3 py-2">{item.fileSize}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="mt-4">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </div>

              <p className="text-xs text-muted text-center mt-2">
                {totalResults} result{totalResults !== 1 ? 's' : ''} total
              </p>
            </div>
          )}
        </div>

        {/* Right content - Results table */}
        <section className="flex-1 overflow-y-auto">
        {logDetail && (
            <LogDetail data={logDetail} />
        )}
        </section>
      </main>
    </div>
  );
};

export default LogsPage;
