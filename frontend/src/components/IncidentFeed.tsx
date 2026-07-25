import React, { useState } from 'react';
import { Incident } from '../types';
import { decodeHtmlEntities, cleanTitle } from '../utils/textUtils';

interface IncidentFeedProps {
  incidents: Incident[];
  isLoading: boolean;
  error: string | null;
  onSelectIncident: (incident: Incident) => void;
}

export const IncidentFeed: React.FC<IncidentFeedProps> = ({
  incidents,
  isLoading,
  error,
  onSelectIncident,
}) => {
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedIds((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-sm font-medium">Fetching intelligence data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-6 text-center my-6">
        <p className="text-red-400 font-semibold mb-2">Error Connection Failure</p>
        <p className="text-sm text-slate-300">{error}</p>
        <p className="text-xs text-slate-500 mt-3">Ensure the FastAPI backend service is active on http://localhost:8001</p>
      </div>
    );
  }

  if (incidents.length === 0) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12 text-center my-6">
        <p className="text-slate-400 font-medium">No conflict incidents matching current filters.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {incidents.map((incident) => {
        const decodedTitle = cleanTitle(incident.title);
        const decodedDescription = decodeHtmlEntities(incident.description);
        const decodedSourceName = decodeHtmlEntities(incident.source_name);
        const isExpanded = !!expandedIds[incident.id];
        const isLongText = decodedDescription.length > 220;

        return (
          <article
            key={incident.id}
            className="bg-slate-900/80 border border-slate-800 hover:border-blue-500/50 rounded-xl p-5 sm:p-6 transition-all shadow-lg hover:shadow-xl group relative"
          >
            {/* Header info bar */}
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex items-center gap-2 flex-wrap">
                {incident.severity && (
                  <span
                    className={`inline-flex items-center gap-1 text-xs font-extrabold px-2.5 py-1 rounded-md border uppercase tracking-wider font-mono shadow-sm ${
                      incident.severity === 'Critical'
                        ? 'bg-red-950 text-red-300 border-red-700'
                        : incident.severity === 'High'
                        ? 'bg-amber-950 text-amber-300 border-amber-700'
                        : incident.severity === 'Low'
                        ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                        : 'bg-blue-950 text-blue-300 border-blue-700'
                    }`}
                  >
                    {incident.severity}
                  </span>
                )}

                {incident.is_darknet ? (
                  <span className="inline-flex items-center gap-1.5 bg-purple-950/90 border border-purple-700 text-purple-300 text-xs font-semibold px-2.5 py-1 rounded-md shadow-sm">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping"></span>
                    Tor / Darknet
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 bg-slate-950 border border-slate-700 text-slate-300 text-xs font-semibold px-2.5 py-1 rounded-md shadow-sm">
                    Clearnet OSINT
                  </span>
                )}

                {incident.is_merged && (
                  <span className="inline-flex items-center gap-1 bg-cyan-950/90 border border-cyan-700 text-cyan-300 text-xs font-bold px-2 py-0.5 rounded-md shadow-sm" title="Περιστατικό ενοποιημένο από πολλαπλές πηγές">
                    🔗 Multi-Source Merged ({incident.sources?.length || 2})
                  </span>
                )}

                <span className="text-xs text-slate-300 font-mono bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                  Source: {decodedSourceName}
                </span>
              </div>

              <time className="text-xs text-slate-400 font-mono shrink-0">
                {new Date(incident.date_reported).toLocaleString()}
              </time>
            </div>

            {/* Title */}
            <h3 
              className="text-lg sm:text-xl font-extrabold text-slate-100 group-hover:text-blue-400 transition-colors mb-3 cursor-pointer leading-snug tracking-tight" 
              onClick={() => onSelectIncident(incident)}
            >
              {decodedTitle}
            </h3>

            {/* AI Summary Banner if present */}
            {incident.summary && (
              <div className="mb-3 bg-cyan-950/30 border-l-4 border-cyan-500 p-3 rounded-r-lg">
                <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-400 block mb-1">
                  🤖 AI Synthesis Summary:
                </span>
                <p className="text-xs sm:text-sm text-cyan-100/90 leading-relaxed font-sans">
                  {incident.summary}
                </p>
              </div>
            )}

            {/* News Description */}
            <div className="mb-4">
              <p className={`text-slate-100 text-base leading-relaxed whitespace-pre-wrap font-sans ${!isExpanded ? 'line-clamp-3' : ''}`}>
                {decodedDescription}
              </p>

              {isLongText && (
                <button
                  onClick={(e) => toggleExpand(incident.id, e)}
                  className="mt-2 text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors focus:outline-none"
                >
                  <span>{isExpanded ? '▲ Απόκρυψη κειμένου (Show less)' : '▼ Επέκταση κειμένου (Read more)'}</span>
                </button>
              )}
            </div>

            {/* Merged Sources List */}
            {incident.sources && incident.sources.length > 1 && (
              <div className="mb-3 text-xs bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                <span className="font-semibold text-slate-400 block mb-1">Συνδεδεμένες Πηγές (Combined Sources):</span>
                <div className="flex flex-wrap gap-2">
                  {incident.sources.map((src, idx) => (
                    <a
                      key={idx}
                      href={src.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:underline bg-slate-900 px-2 py-0.5 rounded border border-slate-700 inline-flex items-center gap-1"
                    >
                      <span>📍 {src.source_name}</span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Actions / Footer */}
            <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onSelectIncident(incident)}
                  className="px-4 py-2 bg-emerald-900/80 hover:bg-emerald-800 border border-emerald-600/80 text-emerald-200 font-bold rounded-lg transition-all inline-flex items-center gap-2 shadow-md hover:shadow-emerald-900/30"
                >
                  <span>🛡️</span>
                  <span>Ανάγνωση Εντός Εφαρμογής (Isolated Reader)</span>
                </button>
              </div>

              <div className="flex items-center gap-2 text-slate-400 font-mono truncate max-w-sm">
                <span className="truncate" title={incident.source_url}>URL: {incident.source_url}</span>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
};
