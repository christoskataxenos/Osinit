import React, { useState } from 'react';
import { Incident } from '../types';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  incidents: Incident[];
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose, incidents }) => {
  const [exportFormat, setExportFormat] = useState<'JSON' | 'CSV'>('JSON');

  if (!isOpen) return null;

  const downloadFile = (content: string, fileName: string, contentType: string) => {
    const a = document.createElement('a');
    const file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const handleExport = () => {
    const timestamp = new Date().toISOString().split('T')[0];
    if (exportFormat === 'JSON') {
      const dataStr = JSON.stringify(incidents, null, 2);
      downloadFile(dataStr, `osinit_incidents_${timestamp}.json`, 'application/json');
    } else {
      // Convert to CSV
      const headers = ['ID', 'Title', 'Severity', 'Source Name', 'Source URL', 'Is Darknet', 'Date Reported', 'Summary'];
      const rows = incidents.map((inc) => [
        `"${inc.id}"`,
        `"${(inc.title || '').replace(/"/g, '""')}"`,
        `"${inc.severity || 'Medium'}"`,
        `"${(inc.source_name || '').replace(/"/g, '""')}"`,
        `"${(inc.source_url || '').replace(/"/g, '""')}"`,
        inc.is_darknet ? 'TRUE' : 'FALSE',
        `"${inc.date_reported}"`,
        `"${(inc.summary || inc.description || '').replace(/"/g, '""')}"`,
      ]);

      const csvContent = [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
      downloadFile(csvContent, `osinit_incidents_${timestamp}.csv`, 'text/csv');
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-xl max-w-md w-full p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span>📥</span> Εξαγωγή Δεδομένων OSINT
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            ✕
          </button>
        </div>

        <div className="py-4 space-y-4">
          <p className="text-sm text-slate-300">
            Επιλέξτε τη μορφή αρχείου για την εξαγωγή των{' '}
            <strong className="text-cyan-400">{incidents.length}</strong> επιλεγμένων περιστατικών:
          </p>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setExportFormat('JSON')}
              className={`p-3 rounded-lg border text-sm font-semibold flex flex-col items-center gap-1 transition-all ${
                exportFormat === 'JSON'
                  ? 'border-cyan-500 bg-cyan-950/40 text-cyan-200 shadow-md'
                  : 'border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600'
              }`}
            >
              <span className="text-base font-mono">{"{ }"}</span>
              <span>JSON Format</span>
            </button>

            <button
              type="button"
              onClick={() => setExportFormat('CSV')}
              className={`p-3 rounded-lg border text-sm font-semibold flex flex-col items-center gap-1 transition-all ${
                exportFormat === 'CSV'
                  ? 'border-cyan-500 bg-cyan-950/40 text-cyan-200 shadow-md'
                  : 'border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600'
              }`}
            >
              <span className="text-base font-mono">📊</span>
              <span>CSV Spreadsheet</span>
            </button>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-colors"
          >
            Ακύρωση
          </button>
          <button
            onClick={handleExport}
            className="px-5 py-2 text-sm font-semibold text-slate-950 bg-cyan-400 hover:bg-cyan-300 rounded-lg shadow-lg transition-colors"
          >
            Κατέβασμα Αρχείου
          </button>
        </div>
      </div>
    </div>
  );
};
