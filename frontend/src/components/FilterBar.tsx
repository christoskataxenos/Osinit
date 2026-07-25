import React from 'react';
import { FilterOption, TimeFilterOption } from '../types';

interface FilterBarProps {
  currentFilter: FilterOption;
  onFilterChange: (filter: FilterOption) => void;
  currentTimeFilter: TimeFilterOption;
  onTimeFilterChange: (timeFilter: TimeFilterOption) => void;
  totalCount: number;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  currentFilter,
  onFilterChange,
  currentTimeFilter,
  onTimeFilterChange,
  totalCount,
}) => {
  return (
    <div className="bg-slate-900/80 backdrop-blur border border-slate-800/80 rounded-xl p-3.5 mb-6 shadow-md flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-2">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
          OSINT Feed:
        </span>
        <span className="bg-slate-800/90 text-xs px-2.5 py-0.5 rounded-full text-slate-300 font-mono border border-slate-700/60">
          {totalCount} Περιστατικά
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2.5">
        {/* Source Filters */}
        <div className="flex items-center gap-1 bg-slate-950/90 p-1 rounded-lg border border-slate-800/80 text-xs">
          <button
            onClick={() => onFilterChange('all')}
            className={`px-3 py-1 font-semibold rounded transition-all ${
              currentFilter === 'all'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            Όλες οι Πηγές
          </button>

          <button
            onClick={() => onFilterChange('clearnet')}
            className={`px-3 py-1 font-semibold rounded transition-all ${
              currentFilter === 'clearnet'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            Clearnet
          </button>

          <button
            onClick={() => onFilterChange('darknet')}
            className={`px-3 py-1 font-semibold rounded transition-all flex items-center gap-1.5 ${
              currentFilter === 'darknet'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-purple-300 animate-pulse"></span>
            Darknet Only
          </button>
        </div>

        {/* Time Window Filters */}
        <div className="flex items-center gap-1 bg-slate-950/90 p-1 rounded-lg border border-slate-800/80 text-xs">
          <span className="text-[11px] font-bold text-slate-500 uppercase px-1.5">Χρόνος:</span>
          <button
            onClick={() => onTimeFilterChange('12h')}
            className={`px-2.5 py-1 font-semibold rounded transition-all ${
              currentTimeFilter === '12h'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            ⏱️ 12ωρο
          </button>

          <button
            onClick={() => onTimeFilterChange('24h')}
            className={`px-2.5 py-1 font-semibold rounded transition-all ${
              currentTimeFilter === '24h'
                ? 'bg-amber-600/90 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            24ωρο
          </button>

          <button
            onClick={() => onTimeFilterChange('all')}
            className={`px-2.5 py-1 font-semibold rounded transition-all ${
              currentTimeFilter === 'all'
                ? 'bg-slate-700 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            Όλα
          </button>
        </div>
      </div>
    </div>
  );
};
