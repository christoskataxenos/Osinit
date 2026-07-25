import React, { useEffect, useState } from 'react';
import { decodeHtmlEntities } from '../utils/textUtils';

interface MasterBriefingModalProps {
  hours: number;
  onClose: () => void;
}

interface MasterBriefingData {
  title: string;
  date: string;
  incidents_analyzed: number;
  briefing_content: string;
  provider_used: string;
}

function renderFormattedMarkdown(text: string) {
  if (!text) return null;
  const lines = text.split('\n');

  return (
    <div className="space-y-4 text-slate-100 font-sans leading-relaxed text-lg">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return null;

        if (trimmed.startsWith('###') || trimmed.startsWith('##')) {
          const headerText = trimmed.replace(/^#+\s*/, '');
          return (
            <div key={idx} className="mt-8 mb-3 pb-2 border-b border-slate-800 flex items-center gap-2.5">
              <span className="text-blue-400 font-bold text-xl">📰</span>
              <h3 className="text-xl sm:text-2xl font-extrabold text-blue-300 tracking-tight">
                {headerText}
              </h3>
            </div>
          );
        }

        if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
          const bulletContent = trimmed.replace(/^[•\-]\s*/, '');
          const parts = bulletContent.split(/\*\*(.*?)\*\*/g);
          return (
            <div key={idx} className="flex items-start gap-3 my-2 pl-2">
              <span className="text-blue-400 text-base mt-1">▪</span>
              <p className="text-slate-200 text-lg">
                {parts.map((part, pIdx) => {
                  if (pIdx % 2 === 1) {
                    return (
                      <strong key={pIdx} className="text-slate-50 font-bold bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700">
                        {part}
                      </strong>
                    );
                  }
                  return part;
                })}
              </p>
            </div>
          );
        }

        const parts = trimmed.split(/\*\*(.*?)\*\*/g);
        return (
          <p key={idx} className="text-slate-200 text-lg leading-relaxed">
            {parts.map((part, pIdx) => {
              if (pIdx % 2 === 1) {
                return (
                  <strong key={pIdx} className="text-slate-50 font-bold bg-slate-800/70 px-1.5 py-0.5 rounded border border-slate-700">
                    {part}
                  </strong>
                );
              }
              return part;
            })}
          </p>
        );
      })}
    </div>
  );
}

export const MasterBriefingModal: React.FC<MasterBriefingModalProps> = ({ hours, onClose }) => {
  const [briefingData, setBriefingData] = useState<MasterBriefingData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    const fetchMasterBriefing = async () => {
      try {
        const response = await fetch(`http://localhost:8001/api/v1/incidents/master-briefing?hours=${hours}`);
        if (!response.ok) {
          throw new Error(`HTTP Error ${response.status}: Failed to generate master briefing`);
        }
        const data: MasterBriefingData = await response.json();
        if (isMounted) {
          setBriefingData(data);
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('Failed to load master briefing');
          }
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchMasterBriefing();

    return () => {
      isMounted = false;
    };
  }, [hours]);

  // ESC key listener & body scroll lock
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  const handleCopyText = () => {
    if (!briefingData) return;
    navigator.clipboard.writeText(decodeHtmlEntities(briefingData.briefing_content));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
      <div 
        className="relative w-full max-w-5xl max-h-[92vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-extrabold rounded-full bg-blue-950 border border-blue-600 text-blue-300 shadow-md">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
              📰 ΣΥΝΘΕΤΙΚΗ ΗΜΕΡΗΣΙΑ ΕΚΘΕΣΗ OSINT (MASTER BRIEFING)
            </span>

            {briefingData && (
              <span className="text-xs text-slate-300 font-mono bg-slate-900 px-3 py-1 rounded-md border border-slate-800">
                📊 Σύνθεση <strong>{briefingData.incidents_analyzed}</strong> Ειδήσεων/Διαρροών
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleCopyText}
              disabled={isLoading || !briefingData}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold rounded-lg border border-slate-600 text-xs shadow-sm"
            >
              <span>{copied ? '✅ Αντιγράφηκε!' : '📋 Αντιγραφή Έκθεσης'}</span>
            </button>

            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* AI Router Notice Banner */}
        {briefingData && (
          <div className="bg-blue-950/80 px-6 py-2.5 border-b border-blue-800 text-xs text-blue-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>✨</span>
              <span>
                <strong>Zero-Key Master AI Writer:</strong> Συντέθηκε αυτόματα από το <code>{briefingData.provider_used}</code> με βάση όλες τις ειδήσεις του τελευταίου {hours}ώρου.
              </span>
            </div>
            <span className="font-mono text-slate-400">{briefingData.date}</span>
          </div>
        )}

        {/* Content Body */}
        <div className="p-6 sm:p-10 overflow-y-auto flex-1 text-slate-100 space-y-6">
          {isLoading ? (
            <div className="py-24 flex flex-col items-center justify-center text-slate-400">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-base font-semibold">Σύνθεση όλων των ειδήσεων σε ενιαία Ημερήσια Έκθεση...</p>
            </div>
          ) : error ? (
            <div className="p-6 bg-red-950/40 border border-red-800 rounded-xl text-red-300">
              <p className="font-bold mb-1">Σφάλμα παραγωγής συνθετικής έκθεσης</p>
              <p>{error}</p>
            </div>
          ) : (
            briefingData && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-50 leading-tight tracking-tight">
                    {briefingData.title}
                  </h2>
                  <p className="text-slate-400 text-sm mt-2 font-mono">
                    Έκδοση OSINT Intelligence Synthesis • Παράθυρο {hours} ώρες
                  </p>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-inner">
                  {renderFormattedMarkdown(briefingData.briefing_content)}
                </div>
              </div>
            )
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <span>OSINT Aggregator Master Daily Briefing</span>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-slate-100 font-bold rounded-lg border border-slate-600"
          >
            Κλείσιμο (Close)
          </button>
        </div>
      </div>
    </div>
  );
};
