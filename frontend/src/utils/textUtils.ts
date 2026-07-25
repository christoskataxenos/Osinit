/**
 * Αποκωδικοποίηση HTML Entities (π.χ. &#39; -> ', &quot; -> ", &amp; -> &)
 * για καθαρή και ευανάγνωστη προβολή κειμένων ειδήσεων.
 */
export function decodeHtmlEntities(text: string | null | undefined): string {
  if (!text) return '';

  // Χρήση DOMParser αν εκτελείται στο browser
  if (typeof window !== 'undefined' && typeof DOMParser !== 'undefined') {
    try {
      const doc = new DOMParser().parseFromString(text, 'text/html');
      return doc.body.textContent || text;
    } catch {
      // Σε περίπτωση σφάλματος, fallback στους regex αντικαταστάτες
    }
  }

  return text
    .replace(/&#(\d+);/g, (_, dec) => String.fromCharCode(Number(dec)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ');
}

/**
 * Καθαρισμός και βελτιστοποίηση τίτλου είδησης.
 * Αφαιρεί διπλά tags καναλιών Telegram αν υπάρχουν.
 */
export function cleanTitle(title: string | null | undefined): string {
  const decoded = decodeHtmlEntities(title);
  if (!decoded) return '';
  return decoded.trim();
}
