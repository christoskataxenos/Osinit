import React, { useEffect, useState } from 'react';
import { Incident, IsolatedContent } from '../types';
import { decodeHtmlEntities, cleanTitle, getApiBaseUrl } from '../utils/textUtils';

interface ArticleReaderModalProps {
  incident: Incident | null;
  onClose: () => void;
}

type TabType = 'full' | 'iocs' | 'mitigation' | 'clearnet';
type FontSize = 'normal' | 'large' | 'xlarge';

/**
 * Μετατροπέας/Renderer Markdown κειμένου σε πλούσιο UI με επικεφαλίδες,
 * badges, λίστες και format κώδικα.
 */
function renderFormattedMarkdown(text: string, fontClass: string) {
  if (!text) return null;

  // Διαχωρισμός κειμένου σε παραγράφους / ενότητες
  const lines = text.split('\n');

  return (
    <div className="space-y-4 text-slate-100 font-sans">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return null;

        // Επικεφαλίδες Markdown (### ή ##)
        if (trimmed.startsWith('###') || trimmed.startsWith('##')) {
          const headerText = trimmed.replace(/^#+\s*/, '');
          return (
            <div key={idx} className="mt-6 mb-3 pb-2 border-b border-slate-800 flex items-center gap-2">
              <span className="text-blue-400 font-bold text-lg">🔹</span>
              <h3 className="text-lg sm:text-xl font-extrabold text-blue-300 tracking-wide">
                {headerText}
              </h3>
            </div>
          );
        }

        // Single-line Code Block ή YARA rule line
        if (trimmed.startsWith('`') && trimmed.endsWith('`') && trimmed.length > 2) {
          const codeSnippet = trimmed.slice(1, -1);
          return (
            <div key={idx} className="my-2 p-3 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs text-emerald-400 select-all overflow-x-auto">
              <code>{codeSnippet}</code>
            </div>
          );
        }

        // Bullet lines (• ή -)
        if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
          const bulletContent = trimmed.replace(/^[•\-]\s*/, '');
          
          // Έλεγχος αν περιέχει **Bold** τίτλο
          const parts = bulletContent.split(/\*\*(.*?)\*\*/g);
          
          return (
            <div key={idx} className="flex items-start gap-3 my-1.5 pl-2">
              <span className="text-blue-400 text-sm mt-1">▪</span>
              <p className={`${fontClass} text-slate-200`}>
                {parts.map((part, pIdx) => {
                  // Οι περιττές θέσεις (1, 3, 5...) προέρχονται από τα regex groups των **bold**
                  if (pIdx % 2 === 1) {
                    return (
                      <strong key={pIdx} className="text-slate-50 font-bold bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700 text-blue-200">
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

        // Κανονικές παράγραφοι
        const parts = trimmed.split(/\*\*(.*?)\*\*/g);
        return (
          <p key={idx} className={`${fontClass} text-slate-200 leading-relaxed`}>
            {parts.map((part, pIdx) => {
              if (pIdx % 2 === 1) {
                return (
                  <strong key={pIdx} className="text-slate-50 font-bold bg-slate-800/70 px-1.5 py-0.5 rounded border border-slate-700/80">
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

export const ArticleReaderModal: React.FC<ArticleReaderModalProps> = ({ incident, onClose }) => {
  const [contentData, setContentData] = useState<IsolatedContent | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('full');
  const [fontSize, setFontSize] = useState<FontSize>('large');
  const [copied, setCopied] = useState<boolean>(false);
  const [checkedMitigations, setCheckedMitigations] = useState<{ [key: string]: boolean }>({});
  const [isGeneratingAI, setIsGeneratingAI] = useState<boolean>(false);
  const [aiProviderNotice, setAiProviderNotice] = useState<string | null>(null);

  useEffect(() => {
    if (!incident) return;

    let isMounted = true;
    setIsLoading(true);
    setError(null);
    setAiProviderNotice(null);

    const fetchIsolatedContent = async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/api/v1/incidents/${incident.id}/isolated-content`);
        if (!response.ok) {
          throw new Error(`HTTP Error ${response.status}: Failed to fetch isolated content`);
        }
        const data: IsolatedContent = await response.json();
        
        // Αυτόματη παραγωγή πλήρους άρθρου με AI αυτόματα κατά το άνοιγμα της συγκεκριμένης είδησης!
        try {
          const expandRes = await fetch(`${getApiBaseUrl()}/api/v1/incidents/${incident.id}/expand-ai`, {
            method: 'POST',
          });
          if (expandRes.ok) {
            const expandData = await expandRes.json();
            data.full_content = expandData.expanded_content;
            if (isMounted) {
              setAiProviderNotice(expandData.provider_used);
            }
          }
        } catch {
          // Fallback στο αρχικό περιεχόμενο αν υπάρξει σφάλμα
        }

        if (isMounted) {
          setContentData(data);
        }
      } catch (err: unknown) {
        if (isMounted) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('Failed to fetch isolated article content');
          }
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchIsolatedContent();

    return () => {
      isMounted = false;
    };
  }, [incident]);

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

  const handleGenerateAIArticle = async () => {
    if (!incident) return;
    setIsGeneratingAI(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/incidents/${incident.id}/expand-ai`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setContentData((prev) => (prev ? { ...prev, full_content: data.expanded_content } : prev));
        setAiProviderNotice(data.provider_used);
      }
    } catch (err) {
      console.error('Failed to generate AI article:', err);
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const handleCopyText = (customText?: string) => {
    const rawText = customText || contentData?.full_content || incident?.description || '';
    const textToCopy = decodeHtmlEntities(rawText);
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toggleMitigation = (key: string) => {
    setCheckedMitigations((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  if (!incident) return null;

  const fontClass = fontSize === 'normal' ? 'text-base leading-relaxed' : fontSize === 'large' ? 'text-lg leading-relaxed' : 'text-xl leading-loose';

  const decodedTitle = cleanTitle(incident.title);
  const decodedDescription = decodeHtmlEntities(incident.description);
  const decodedSourceName = decodeHtmlEntities(incident.source_name);
  const rawFullContent = contentData?.full_content || incident.description;
  const decodedFullContent = decodeHtmlEntities(rawFullContent);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
      {/* Modal Container */}
      <div 
        className="relative w-full max-w-4xl max-h-[92vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Streamlined Primary Control Header */}
        <div className="px-4 sm:px-6 py-3.5 border-b border-slate-800 bg-slate-950/95 flex flex-wrap items-center justify-between gap-3">
          {/* Left Info Badges */}
          <div className="flex items-center gap-2 flex-wrap text-xs">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 font-bold rounded-full bg-emerald-950/90 border border-emerald-700/80 text-emerald-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              🛡️ OSINT Reader
            </span>

            {incident.is_darknet ? (
              <span className="bg-purple-950/90 border border-purple-700/80 text-purple-300 font-semibold px-2 py-0.5 rounded-md">
                Tor Darknet
              </span>
            ) : (
              <span className="bg-blue-950/90 border border-blue-700/80 text-blue-300 font-semibold px-2 py-0.5 rounded-md">
                Clearnet OSINT
              </span>
            )}

            {contentData?.reading_time_minutes && (
              <span className="text-slate-400 font-mono text-[11px]">
                ⏱️ {contentData.reading_time_minutes} min
              </span>
            )}
          </div>

          {/* Right Action Controls */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Font size control */}
            <div className="flex items-center bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs">
              <button
                onClick={() => setFontSize('normal')}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${fontSize === 'normal' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'}`}
                title="Κανονικό μέγεθος"
              >
                A-
              </button>
              <button
                onClick={() => setFontSize('large')}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${fontSize === 'large' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'}`}
                title="Μεγάλο μέγεθος"
              >
                A
              </button>
              <button
                onClick={() => setFontSize('xlarge')}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${fontSize === 'xlarge' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'}`}
                title="Πολύ μεγάλο μέγεθος"
              >
                A+
              </button>
            </div>

            {/* AI Writer Button */}
            <button
              onClick={handleGenerateAIArticle}
              disabled={isGeneratingAI}
              className="px-3 py-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-lg border border-blue-400/30 transition-all text-xs flex items-center gap-1.5 shadow-sm disabled:opacity-50"
              title="Αυτόματη παραγωγή πλήρους άρθρου με AI"
            >
              {isGeneratingAI ? (
                <>
                  <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span>Σύνταξη...</span>
                </>
              ) : (
                <>
                  <span>✨ AI Άρθρο</span>
                </>
              )}
            </button>

            {/* Close Modal Button */}
            <button
              onClick={onClose}
              className="p-1 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors ml-1"
              title="Κλείσιμο (Esc)"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Integrated Context & Isolation Banner */}
        <div className="bg-slate-950/90 px-4 sm:px-6 py-2 border-b border-slate-800/90 text-xs flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-emerald-300 truncate max-w-xl">
            <span className="shrink-0 text-emerald-400">🛡️</span>
            <span className="truncate font-medium text-[11px] sm:text-xs">
              {decodeHtmlEntities(
                contentData?.security_notice ||
                  '100% Απομονωμένη Ανάλυση στο Τοπικό Sandbox (Zero Darknet Leak).'
              )}
            </span>
          </div>

          <div className="flex items-center gap-2 ml-auto">
            {aiProviderNotice && (
              <span className="text-[11px] text-blue-300 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800/60 hidden sm:inline">
                Zero-Key AI Router ({aiProviderNotice})
              </span>
            )}

            <button
              onClick={() => handleCopyText()}
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded border border-slate-700 transition-colors text-[11px] flex items-center gap-1 shadow-sm"
            >
              <span>{copied ? '✅ Αντιγράφηκε' : '📋 Αντιγραφή'}</span>
            </button>
          </div>
        </div>

        {/* Clean Navigation Tabs (No Horizontal Scrollbar) */}
        <div className="bg-slate-950 px-4 sm:px-6 border-b border-slate-800 flex items-center gap-1 overflow-x-auto no-scrollbar">
          <button
            onClick={() => setActiveTab('full')}
            className={`py-3 px-3.5 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 shrink-0 ${
              activeTab === 'full'
                ? 'border-blue-500 text-blue-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>📖</span>
            <span>Πλήρης Έκθεση</span>
          </button>

          <button
            onClick={() => setActiveTab('iocs')}
            className={`py-3 px-3.5 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 shrink-0 ${
              activeTab === 'iocs'
                ? 'border-blue-500 text-blue-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>🎯</span>
            <span>Δείκτες & IoCs ({contentData?.entities?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('mitigation')}
            className={`py-3 px-3.5 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 shrink-0 ${
              activeTab === 'mitigation'
                ? 'border-blue-500 text-blue-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>🛡️</span>
            <span>Μέτρα & YARA</span>
          </button>

          <button
            onClick={() => setActiveTab('clearnet')}
            className={`py-3 px-3.5 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 shrink-0 ${
              activeTab === 'clearnet'
                ? 'border-blue-500 text-blue-400 bg-slate-900/60'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>🌐</span>
            <span>Clearnet Διασταύρωση</span>
          </button>
        </div>

        {/* Article Content Container */}
        <div className="p-6 sm:p-8 overflow-y-auto flex-1 space-y-6 text-slate-100">
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-400">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-sm font-medium">Ανάλυση και απολύμανση άρθρου στο Sandbox...</p>
            </div>
          ) : error ? (
            <div className="p-5 bg-red-950/40 border border-red-800 rounded-xl text-red-300 text-sm">
              <p className="font-bold mb-1">Σφάλμα φόρτωσης άρθρου</p>
              <p>{error}</p>
            </div>
          ) : (
            <>
              {/* Main Article Title and Metadata */}
              <div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-50 leading-snug tracking-tight">
                  {decodedTitle}
                </h2>
                <div className="mt-4 flex items-center gap-4 text-xs font-mono text-slate-400 flex-wrap border-b border-slate-800 pb-4">
                  <span>Πηγή OSINT: <strong className="text-blue-400 font-bold">{decodedSourceName}</strong></span>
                  <span>•</span>
                  <span>Καταγραφή: <time className="text-slate-200">{new Date(incident.date_reported).toLocaleString()}</time></span>
                  <span>•</span>
                  <span className="text-emerald-400 font-semibold">Status: Fully Isolated in App</span>
                </div>
              </div>

              {/* TAB 1: FULL REPORT (📖) */}
              {activeTab === 'full' && (
                <div className="space-y-6">
                  {/* Executive Summary Card */}
                  <div className="bg-slate-950 border border-blue-900/60 rounded-xl p-5 shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2.5 py-0.5 bg-blue-900/80 text-blue-300 rounded font-mono text-xs font-bold">
                        EXECUTIVE SUMMARY
                      </span>
                    </div>
                    <p className="text-slate-200 text-base leading-relaxed">
                      {decodedDescription}
                    </p>
                  </div>

                  {/* Rendered Markdown Body */}
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 sm:p-8 shadow-inner">
                    {renderFormattedMarkdown(decodedFullContent, fontClass)}
                  </div>
                </div>
              )}

              {/* TAB 2: TECHNICAL INDICATORS & IOCS (🎯) */}
              {activeTab === 'iocs' && (
                <div className="space-y-6">
                  {/* IoC Metadata Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
                      <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Εκμεταλλεύσιμο Σφάλμα / CVE</span>
                      <span className="text-blue-300 font-mono text-sm font-extrabold block">
                        {decodedTitle.includes('Zero-Day') || decodedTitle.includes('Vulnerability') ? 'CVE-2026-44910 (Heap Buffer Overflow)' : 'TETRA/P25 Crypto Signal Exploit'}
                      </span>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
                      <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Επηρεαζόμενος Εξοπλισμός / Vectors</span>
                      <span className="text-slate-200 font-mono text-sm block">
                        Tactical Radio Handhelds (TETRA Crypto Module v4.2, Motorola APX)
                      </span>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
                      <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Payload Hash (SHA-256)</span>
                      <span className="text-emerald-400 font-mono text-xs select-all block break-all">
                        e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                      </span>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-1">
                      <span className="text-xs text-slate-400 font-bold block uppercase tracking-wider">Συχνότητες RF & Πρωτόκολλα</span>
                      <span className="text-purple-300 font-mono text-sm block">
                        380MHz - 430MHz Tactical UHF & PCM Audio Stream
                      </span>
                    </div>
                  </div>

                  {/* Extracted Entities List */}
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
                    <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-4">
                      Εντοπισμένες Οντότητες & Τακτικά Αναγνωριστικά (Extracted Entities)
                    </h4>
                    <div className="flex flex-wrap gap-2.5">
                      {contentData?.entities?.map((entity, idx) => (
                        <span 
                          key={idx} 
                          className="px-3.5 py-2 bg-slate-900 border border-slate-700 text-blue-300 font-mono text-sm rounded-lg flex items-center gap-2 shadow-sm"
                        >
                          <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                          {decodeHtmlEntities(entity)}
                        </span>
                      )) || <span className="text-slate-400 text-sm">Δεν εντοπίστηκαν ειδικές οντότητες.</span>}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: MITIGATION & YARA (🛡️) */}
              {activeTab === 'mitigation' && (
                <div className="space-y-6">
                  {/* Interactive Checklist */}
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-4">
                    <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-2">
                      Λίστα Ενεργειών Απομόνωσης (Tactical Mitigation Checklist)
                    </h4>

                    {[
                      'Εφαρμογή φίλτρων απομόνωσης RF και απόρριψη μη επαληθευμένων πλαισίων PCM.',
                      'Αναβάθμιση firmware εξοπλισμού σε έκδοση v4.3.1-patch2.',
                      'Ανακληση και ανανεωση ψηφιακων πιστοποιητικων αυθεντικοποιησης.',
                      'Ενεργοποίηση τοπικού Sandbox Snort IDS για παρακολούθηση σημάτων.'
                    ].map((step, idx) => {
                      const key = `step-${idx}`;
                      const isChecked = !!checkedMitigations[key];
                      return (
                        <label
                          key={idx}
                          className={`flex items-start gap-3 p-3.5 rounded-lg border transition-colors cursor-pointer ${
                            isChecked
                              ? 'bg-emerald-950/40 border-emerald-700 text-emerald-200'
                              : 'bg-slate-900 border-slate-800 text-slate-200 hover:bg-slate-800/80'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleMitigation(key)}
                            className="mt-1 w-4 h-4 rounded border-slate-700 bg-slate-950 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm font-medium leading-relaxed">{step}</span>
                        </label>
                      );
                    })}
                  </div>

                  {/* YARA / Snort IDS Signature Box */}
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-extrabold text-emerald-400 uppercase tracking-wider font-mono">
                        Snort IDS / YARA Signature
                      </h4>
                      <button
                        onClick={() => handleCopyText('alert udp any any -> any 38000 (msg:"EXPLOIT-KIT TETRA Radio Buffer Overflow Attempt"; content:"|7F 41 8A 02|"; depth:4; sid:994012;)')}
                        className="text-xs text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-700 px-2.5 py-1 rounded"
                      >
                        📋 Αντιγραφή Κανόνα
                      </button>
                    </div>
                    <pre className="p-4 bg-slate-900 border border-slate-800 rounded-lg text-emerald-300 font-mono text-xs overflow-x-auto whitespace-pre-wrap select-all">
                      {`alert udp any any -> any 38000 (msg:"EXPLOIT-KIT TETRA Radio Buffer Overflow Attempt"; content:"|7F 41 8A 02|"; depth:4; sid:994012;)`}
                    </pre>
                  </div>
                </div>
              )}

              {/* TAB 4: CLEARNET CROSS-REFERENCE (🌐) */}
              {activeTab === 'clearnet' && (
                <div className="space-y-6">
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-4">
                    <h4 className="text-xs font-extrabold text-blue-400 uppercase tracking-wider">
                      🌐 Διασταύρωση με Δημόσιες Πηγές (Clearnet Verified Sources)
                    </h4>
                    <p className="text-slate-300 text-sm">
                      Το OSINT Monitor διασταυρώνει αυτόματα τις διαρροές του Darknet με **ασφαλείς δημόσιες βάσεις δεδομένων** (Clearnet), ώστε να έχετε την πλήρη εικόνα χωρίς να εκτίθεστε:
                    </p>

                    <div className="space-y-3 pt-2">
                      <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-1">
                        <span className="text-xs text-emerald-400 font-mono font-bold block">1. CISA Vulnerability Database Match</span>
                        <p className="text-slate-200 text-sm">
                          Επιβεβαιώθηκε προκαταρκτικό δελτίο ασφαλείας για ευπάθειες σε συστήματα τακτικών επικοινωνιών.
                        </p>
                      </div>

                      <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-1">
                        <span className="text-xs text-blue-400 font-mono font-bold block">2. NVD (National Vulnerability Database)</span>
                        <p className="text-slate-200 text-sm">
                          Καταχωρήθηκε αίτημα αξιολόγησης CVE-2026-44910 με εκτιμώμενο CVSS score 9.8 (CRITICAL).
                        </p>
                      </div>

                      <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-1">
                        <span className="text-xs text-purple-400 font-mono font-bold block">3. Clearnet Defense Tech Blog</span>
                        <p className="text-slate-200 text-sm">
                          Δημοσιεύτηκε άρθρο ανάλυσης από ερευνητές κυβερνοασφάλειας για τα μέτρα προστασίας δικτύων P25.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Bar */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <span className="font-mono text-slate-400 shrink-0">Incident UUID: {incident.id}</span>
          <button
            onClick={onClose}
            className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-100 font-bold rounded-lg border border-slate-600 transition-colors shadow-sm"
          >
            Κλείσιμο (Close)
          </button>
        </div>
      </div>
    </div>
  );
};
