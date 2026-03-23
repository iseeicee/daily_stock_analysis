
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
  // Set page title
  useEffect(() => {
    document.title = '日志 - DSA';
  }, []);

  // Input state
  const [isRunning, setIsRunning] = useState(false);
  const [logDetail, setLogDetailResult] = useState<LogDetailResponse | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  // Results state
  const [results, setResults] = useState<LogInfo[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pointer, setPointer] = useState(0);
  const [isLoadingResults, setIsLoadingResults] = useState(false);
  const pageSize = 13;

  // Fetch results
  const fetchResults = useCallback(async (page = 1, code?: string) => {
    setIsLoadingResults(true);
    try {
      const response = await logsApi.getResults({ code: code || undefined, page, limit: pageSize });
      setResults(response.items);
      setTotalResults(response.total);
      setCurrentPage(response.page);
    } catch (err) {
      console.error('Failed to fetch log list:', err);
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
  const getLogDetail = async (fileName: string, init?: boolean) => {
    try {
      setIsRunning(true);
      fileName = fileName.trim();
      const response = await logsApi.getLogDetail(fileName, init?0:pointer);
      setLogDetailResult(response?response:null);
      setPointer(response?response.pointer:0);
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
    <div className="items-center gap-4 px-3 py-2 rounded-lg bg-elevated border border-white/5 text-xs font-mono animate-fade-in">
      <span className="text-secondary-text">File Name: <span className="text-cyan">{data.fileName}</span></span>
      {/* <span className="text-secondary-text pl-3">Pointer: <span className="text-cyan">{data.pointer}</span></span> */}
      <div className="log-content">{data.content.map((line) => (
          <p className="text-foreground">{line}</p>
      ))}
        {/* <span className="text-secondary-text"><a onClick={() => getLogDetail(data.fileName)}>Load More</a></span> */}
      </div>
      <div>
        {pointer > 0 && (
          <span className="text-cyan"><button className="log-item" onClick={() => getLogDetail(data.fileName)} disabled={isRunning}>Load More</button></span>
        )}
      </div>
      {runError && (
        <span className="text-secondary-text">Errors: <span className="text-red-400">{runError}</span></span>
      )}
    </div>
  );

  return (
    <div className="min-h-full flex flex-col rounded-[1.5rem] bg-transparent">

      {/* Main content */}
      <main className="flex min-h-0 flex-1 flex-col gap-3 overflow-hidden p-3 lg:flex-row">
        {/* Left sidebar - Performance */}
        <div className="flex max-h-[38vh] flex-col gap-3 overflow-y-auto lg:max-h-none lg:w-60 lg:flex-shrink-0">
{isLoadingResults ? (
            <div className="flex flex-col items-center justify-center h-64">
              <div className="w-10 h-10 border-3 border-cyan/20 border-t-cyan rounded-full animate-spin" />
              <p className="mt-3 text-secondary-text text-sm">Loading results...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-12 h-12 mb-3 rounded-xl bg-elevated flex items-center justify-center">
                <svg className="w-6 h-6 text-muted-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-base font-medium text-foreground mb-1.5">No Results</h3>
              <p className="text-xs text-muted-text max-w-xs">
                No content to display.
              </p>
            </div>
          ) : (
            <div className="animate-fade-in">
              <div className="rounded-xl bg-card/72">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-elevated text-left">
                      {/* <th className="px-3 py-2.5 text-xs font-medium text-secondary-text uppercase tracking-wider">FileDate</th> */}
                      <th className="px-3 py-2.5 text-xs font-medium text-secondary-text uppercase tracking-wider">File List</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((item) => (
                      <tr
                        key={item.fileName}
                        className="border-t border-white/5 transition-colors hover:bg-hover"
                      >
                        {/* <td className="px-3 py-2 font-mono text-cyan text-xs">{item.createdAt}</td> */}
                        <td className="px-3 py-2 log-item" onClick={() => getLogDetail(item.fileName, true)}>
                          <p>{item.createdAt} [{item.fileSize} MB]</p>
                          <p>{item.fileName}</p>
                        </td>
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

              <p className="text-xs text-muted-text text-center mt-2">
                {totalResults} result{totalResults !== 1 ? 's' : ''} total
              </p>
            </div>
          )}
        </div>

        {/* Right content - Results table */}
        <section className="min-h-0 flex-1 overflow-y-auto log-content-width">
          {isRunning ? (
            <div className="flex flex-col items-center justify-center h-64">
              <div className="w-10 h-10 border-3 border-cyan/20 border-t-cyan rounded-full animate-spin" />
              <p className="mt-3 text-secondary-text text-sm">Loading results...</p>
            </div>
          ) : !logDetail ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-12 h-12 mb-3 rounded-xl bg-elevated flex items-center justify-center">
                <svg className="w-6 h-6 text-muted-text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-base font-medium text-foreground mb-1.5">No Results</h3>
              <p className="text-xs text-muted-text max-w-xs">
                No content to display.
              </p>
            </div>
          ) : (
            <LogDetail data={logDetail} />
        )}
        </section>
      </main>
    </div>
  );
};

export default LogsPage;
