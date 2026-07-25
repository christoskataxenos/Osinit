import React, { useState, useEffect, useCallback } from 'react';
import { Incident, FilterOption, TimeFilterOption } from '../types';
import { FilterBar } from './FilterBar';
import { IncidentFeed } from './IncidentFeed';
import { ArticleReaderModal } from './ArticleReaderModal';
import { MasterBriefingModal } from './MasterBriefingModal';
import { ToastContainer, ToastMessage } from './Toast';
import { ExportModal } from './ExportModal';
import { useWebSocket } from '../hooks/useWebSocket';

export const Dashboard: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [filter, setFilter] = useState<FilterOption>('all');
  const [timeFilter, setTimeFilter] = useState<TimeFilterOption>('12h');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [showMasterBriefing, setShowMasterBriefing] = useState<boolean>(false);
  const [showExportModal, setShowExportModal] = useState<boolean>(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const handleIncidentCreated = useCallback((newIncident: Incident) => {
    setIncidents((prev) => [newIncident, ...prev.filter((i) => i.id !== newIncident.id)]);
    setToasts((prev) => [
      {
        id: `toast-${Date.now()}-${Math.random()}`,
        type: 'CREATED',
        title: newIncident.title,
        message: newIncident.summary || newIncident.description,
        severity: newIncident.severity,
      },
      ...prev,
    ]);
  }, []);

  const handleIncidentUpdated = useCallback((updatedIncident: Incident) => {
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === updatedIncident.id ? updatedIncident : inc))
    );
    setToasts((prev) => [
      {
        id: `toast-${Date.now()}-${Math.random()}`,
        type: 'UPDATED',
        title: `Ενημέρωση: ${updatedIncident.title}`,
        message: updatedIncident.summary || 'Προστέθηκε νέα πηγή στο συμβάν.',
        severity: updatedIncident.severity,
      },
      ...prev,
    ]);
  }, []);

  const { status: wsStatus } = useWebSocket({
    onIncidentCreated: handleIncidentCreated,
    onIncidentUpdated: handleIncidentUpdated,
  });

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const fetchIncidents = useCallback(async (currentFilter: FilterOption, currentTimeFilter: TimeFilterOption) => {
    setIsLoading(true);
    setError(null);

    const queryParams: string[] = [];

    if (currentFilter === 'darknet') {
      queryParams.push('is_darknet=true');
    } else if (currentFilter === 'clearnet') {
      queryParams.push('is_darknet=false');
    }

    if (currentTimeFilter === '12h') {
      queryParams.push('hours=12');
    } else if (currentTimeFilter === '24h') {
      queryParams.push('hours=24');
    }

    const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
    const url = `http://localhost:8001/api/v1/incidents${queryString}`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }
      const data: Incident[] = await response.json();
      setIncidents(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load incidents');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents(filter, timeFilter);
    
    // Auto refresh fallback every 30 seconds if WS is disconnected
    const interval = setInterval(() => {
      fetchIncidents(filter, timeFilter);
    }, 30000);

    return () => clearInterval(interval);
  }, [filter, timeFilter, fetchIncidents]);

  const hoursNumber = timeFilter === '12h' ? 12 : timeFilter === '24h' ? 24 : 168;

  const renderWsBadge = () => {
    switch (wsStatus) {
      case 'CONNECTED':
        return (
          <span className="bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 text-[10px] px-2 py-0.5 rounded-md font-mono font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            LIVE WS
          </span>
        );
      case 'RECONNECTING':
      case 'CONNECTING':
        return (
          <span className="bg-amber-950/80 text-amber-400 border border-amber-800/60 text-[10px] px-2 py-0.5 rounded-md font-mono font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
            RECONNECTING
          </span>
        );
      default:
        return (
          <span className="bg-slate-800 text-slate-400 border border-slate-700 text-[10px] px-2 py-0.5 rounded-md font-mono font-bold uppercase tracking-wider">
            POLLING
          </span>
        );
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Toast Notification Floating Container */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      {/* Header section */}
      <header className="mb-6 border-b border-slate-800/80 pb-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-100">
              OSINT Conflict Monitor
            </h1>
            <span className="bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 text-[10px] px-2 py-0.5 rounded-md font-mono font-bold uppercase tracking-wider">
              BETA
            </span>
            {renderWsBadge()}
          </div>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Standalone Local OSINT Aggregator for Monitoring Armed Conflicts & Darknet Feeds
          </p>
        </div>

        <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap">
          <button
            onClick={() => setShowExportModal(true)}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs sm:text-sm font-semibold rounded-lg border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm"
            title="Εξαγωγή φιλτραρισμένων δεδομένων σε CSV ή JSON"
          >
            <span>📥 Export</span>
          </button>

          <button
            onClick={() => setShowMasterBriefing(true)}
            className="px-3.5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs sm:text-sm font-bold rounded-lg border border-blue-400/30 transition-all flex items-center gap-2 shadow-md"
            title="Δημιουργία ενιαίας συνθετικής εφημερίδας/έκθεσης από όλες τις ειδήσεις"
          >
            <span>📰 Ημερήσια Έκθεση</span>
          </button>

          <button
            onClick={() => fetchIncidents(filter, timeFilter)}
            className="px-3 py-2 bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs sm:text-sm font-medium rounded-lg border border-slate-700 transition-colors flex items-center gap-2 shadow-sm"
          >
            <span>↻ Refresh</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <FilterBar
          currentFilter={filter}
          onFilterChange={setFilter}
          currentTimeFilter={timeFilter}
          onTimeFilterChange={setTimeFilter}
          totalCount={incidents.length}
        />

        <IncidentFeed
          incidents={incidents}
          isLoading={isLoading}
          error={error}
          onSelectIncident={setSelectedIncident}
        />
      </main>

      {/* In-App Isolated Article Reader Modal */}
      {selectedIncident && (
        <ArticleReaderModal
          incident={selectedIncident}
          onClose={() => setSelectedIncident(null)}
        />
      )}

      {/* Synthesized Master Daily Briefing Modal */}
      {showMasterBriefing && (
        <MasterBriefingModal
          hours={hoursNumber}
          onClose={() => setShowMasterBriefing(false)}
        />
      )}

      {/* Analyst Data Export Modal */}
      {showExportModal && (
        <ExportModal
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          incidents={incidents}
        />
      )}
    </div>
  );
};

