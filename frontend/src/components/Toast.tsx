import React, { useEffect } from 'react';

export interface ToastMessage {
  id: string;
  type: 'CREATED' | 'UPDATED' | 'INFO';
  title: string;
  message: string;
  severity?: 'Low' | 'Medium' | 'High' | 'Critical';
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col space-y-3 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ toast: ToastMessage; onDismiss: (id: string) => void }> = ({
  toast,
  onDismiss,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id);
    }, 5000);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const getSeverityBadge = () => {
    switch (toast.severity) {
      case 'Critical':
        return 'bg-red-900/80 text-red-200 border-red-700';
      case 'High':
        return 'bg-amber-900/80 text-amber-200 border-amber-700';
      case 'Medium':
        return 'bg-blue-900/80 text-blue-200 border-blue-700';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="pointer-events-auto bg-slate-900/95 border border-slate-700/80 rounded-lg p-4 shadow-xl backdrop-blur-md transition-all duration-300 transform translate-x-0 animate-bounce-short">
      <div className="flex items-start justify-between space-x-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              {toast.type === 'CREATED' ? '🚨 Νέο Περιστατικό' : '🔄 Ενημέρωση / Merge'}
            </span>
            {toast.severity && (
              <span className={`text-[10px] px-2 py-0.5 rounded border font-mono ${getSeverityBadge()}`}>
                {toast.severity}
              </span>
            )}
          </div>
          <h4 className="text-sm font-semibold text-slate-100 line-clamp-1">{toast.title}</h4>
          <p className="text-xs text-slate-400 mt-1 line-clamp-2">{toast.message}</p>
        </div>
        <button
          onClick={() => onDismiss(toast.id)}
          className="text-slate-500 hover:text-slate-300 text-sm p-1 transition-colors"
          aria-label="Close Toast"
        >
          ✕
        </button>
      </div>
    </div>
  );
};
