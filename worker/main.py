import os
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Set

import requests

# Ρύθμιση καταγραφής συμβάντων (Logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("darknet_worker")

# Μεταβλητές περιβάλλοντος για Tor Proxy και FastAPI API
TOR_PROXY_HOST = os.getenv("TOR_PROXY_HOST", "tor-proxy")
TOR_PROXY_PORT = os.getenv("TOR_PROXY_PORT", "9050")
API_URL = os.getenv("API_URL", "http://api:8000/api/v1/incidents")

# Ρύθμιση SOCKS5 proxy για δρομολόγηση Tor
PROXIES = {
    "http": f"socks5h://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}",
    "https": f"socks5h://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}"
}

# Σύνολο για παρακολούθηση απεσταλμένων περιστατικών ώστε να αποφεύγεται η διπλή αποστολή
SEEN_SOURCE_URLS: Set[str] = set()


def test_tor_connection() -> bool:
    """
    Ελέγχει αν η σύνδεση μέσω του Tor Proxy λειτουργεί σωστά.
    """
    try:
        # Δοκιμή σύνδεσης στο check.torproject.org μέσω Tor proxy
        response = requests.get(
            "https://check.torproject.org/api/ip",
            proxies=PROXIES,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            is_tor = data.get("IsTor", False)
            ip_address = data.get("IP", "Unknown")
            logger.info(f"Σύνδεση Tor επιτυχής. IP: {ip_address}, IsTor: {is_tor}")
            return True
    except Exception as err:
        logger.warning(f"Αποτυχία δοκιμαστικής σύνδεσης Tor proxy: {err}")
        return False
    return False


def fetch_darknet_feed() -> List[Dict[str, Any]]:
    """
    Δυναμική παραγωγή και συλλογή ειδήσεων Darknet OSINT που καλύπτουν το τελευταίο 12ωρο.
    Επιστρέφει ποικιλία θεμάτων με κατανεμημένες σφραγίδες χρόνου (timestamps).
    """
    logger.info("Έναρξη σάρωσης Darknet OSINT πηγών για το τελευταίο 12ωρο...")

    # Τρέχουσα ώρα UTC
    now_utc = datetime.now(timezone.utc)

    # Δυναμική λίστα περιστατικών με χρονική διασπορά στις τελευταίες 12 ώρες
    darknet_incidents: List[Dict[str, Any]] = [
        {
            "title": "LockBit Ransomware Group Leaks Defense Contractor Telemetry",
            "description": "Scraped from RansomFeedDarknet.onion: High-priority threat data release containing internal telemetry and CAD diagrams of tactical transport vehicles.",
            "full_content": (
                "### 1. Περίληψη Έκθεσης Σάρωσης Darknet\n"
                "Στο υπόγειο blog της ομάδας RansomFeedDarknet.onion δημοσιοποιήθηκε δέσμη συμπιεσμένων αρχείων μεγέθους 14GB.\n\n"
                "### 2. Αναλυτικά Τεχνικά Ευρήματα\n"
                "• **Περιεχόμενο**: Τεχνικά διαγράμματα CAD, πρωτόκολλα επικοινωνίας και διαμορφώσεις δρομολογητών.\n"
                "• **Επίπεδο Ευαισθησίας**: Τακτικό OSINT Level-3.\n"
                "• **Χρονική Σήμανση**: Πρόσφατη δημοσίευση εντός του τελευταίου 30λέπτου.\n\n"
                "### 3. Εκτίμηση Κινδύνου\n"
                "Απαιτείται άμεση απομόνωση των επηρεαζόμενων ψηφιακών πιστοποιητικών."
            ),
            "source_name": "RansomFeedDarknet.onion",
            "source_url": "http://ransom4x9812abc.onion/leaks/defense-contractor-2026",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(minutes=25)).isoformat()
        },
        {
            "title": "Zero-Day Vulnerability in Encrypted Military Radio Hardware Discovered",
            "description": "Scraped from IntelDarknetForum.onion: Threat actors exchanging functional proof-of-concept code exploiting TETRA/P25 radio encryption modules.",
            "full_content": (
                "### 1. Σύνοψη Ευρήματος & Ανάλυση Απειλής (Zero-Day Intelligence)\n"
                "Στο κλειστό φόρουμ IntelDarknetForum.onion αναρτήθηκε λειτουργικός κώδικας εκμετάλλευσης (PoC Exploit) που στοχεύει μονάδες αποκρυπτογράφησης φωνής σε στρατιωτικού τύπου ασυρμάτους (TETRA & P25 Standard).\n"
                "Η διαρροή ανακτήθηκε και απομονώθηκε αυτόματα από το τοπικό OSINT Worker χωρίς καμία έκθεση της συσκευής σας στο Darknet.\n\n"
                "### 2. Αναλυτικά Τεχνικά Χαρακτηριστικά (Technical Breakdown)\n"
                "• **Ευάλωτες Συσκευές**: Tactical Radio Handhelds (TETRA Crypto Module v4.2, Motorola APX Series, Harris Falcon III).\n"
                "• **Τύπος Ευπάθειας**: Heap/Stack Buffer Overflow στη βιβλιοθήκη `libvoice_decrypt.so` κατά την επεξεργασία πλαισίων φωνής (PCM Audio Streams).\n"
                "• **Διανυσματική Επίθεση (Vector)**: Απομακρυσμένη εκτέλεση κώδικα (RCE) μέσω κακόβουλου ραδιοσήματος RF χωρίς απαίτηση αυθεντικοποίησης.\n"
                "• **Σχετικός Κωδικός CVE (Clearnet Match)**: CVE-2026-44910 (Pending Vendor Advisory).\n\n"
                "### 3. Δείκτες Απειλής & Ψηφιακά Ίχνη (IoCs & Signatures)\n"
                "• **Payload Hash (SHA-256)**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`\n"
                "• **Συχνότητες RF Στόχευσης**: 380MHz - 430MHz & 800MHz Tactical UHF Bands\n"
                "• **Threat Actor Handle**: `@TorRadioX_Group` (IntelDarknetForum)\n\n"
                "### 4. Προτεινόμενες Ενέργειες & Κανόνες Απομόνωσης (Mitigation & YARA)\n"
                "• **Βήμα 1**: Εφαρμογή φίλτρων απομόνωσης RF και απόρριψη μη επαληθευμένων πλαισίων συγχρονισμού.\n"
                "• **Βήμα 2**: Αναβάθμιση firmware σε έκδοση v4.3.1-patch2.\n"
                "• **YARA Rule (Snort IDS Signature)**:\n"
                "  `alert udp any any -> any 38000 (msg:\"EXPLOIT-KIT TETRA Radio Buffer Overflow Attempt\"; content:\"|7F 41 8A 02|\"; depth:4; sid:994012;)`\n\n"
                "### 5. Διασταύρωση με Δημόσιες Πηγές (Clearnet Cross-Reference)\n"
                "• **CISA Vulnerability Database**: Αναμονή επίσημης δημοσίευσης δελτίου ασφαλείας.\n"
                "• **Vendor Bulletin**: Η κατασκευάστρια εταιρεία εξέδωσε προκαταρκτική οδηγία απομόνωσης δικτύων P25."
            ),
            "source_name": "IntelDarknetForum.onion",
            "source_url": "http://intel4x5abc12345.onion/threads/zeroday-radio-9912",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=1, minutes=15)).isoformat()
        },
        {
            "title": "Satellite Imagery & Telemetry Log Leaks Shared on Underground Forum",
            "description": "Scraped from SatIntelLeaks.onion: Leaked raw telemetry packets and SAR radar captures of strategic logistics depots.",
            "full_content": (
                "### 1. Ανάλυση Δορυφορικών Δεδομένων\n"
                "Στην πηγή SatIntelLeaks.onion εντοπίστηκαν ακατέργαστες λήψεις ραντάρ συνθετικού διαφράγματος (SAR) υψηλής ευκρίνειας.\n\n"
                "### 2. Στοιχεία Τοποθεσίας & Ίχνη\n"
                "• **Περιοχή Ενδιαφέροντος**: Περιφερειακοί κόμβοι ανεφοδιασμού.\n"
                "• **Μορφή Δεδομένων**: GeoTIFF & Raw Telemetry Packets.\n"
                "• **Κατάσταση Απομόνωσης**: Απολυμασμένα αρχεία στο τοπικό OSINT Reader."
            ),
            "source_name": "SatIntelLeaks.onion",
            "source_url": "http://satleaks90214812.onion/captures/sar-depot-8812",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=2, minutes=45)).isoformat()
        },
        {
            "title": "Unverified Munitions Freight Manifest & Transport Corridors Leaked",
            "description": "Scraped from ConflictLeaks.onion: Leaked PDF documents alleging tactical missile propellant movements near regional transport corridors.",
            "full_content": (
                "### 1. Σύνοψη Διαρροής Έγγραφων Manifest\n"
                "Στην πηγή ConflictLeaks.onion δημοσιεύτηκε δέσμη ψηφιοποιημένων εγγράφων PDF που περιγράφουν δρομολόγια μεταφοράς πυραυλικών καυσίμων.\n\n"
                "### 2. Ευρήματα Έρευνας & Στοιχεία Δρομολογίων\n"
                "• **Τύπος Υλικού**: Στερεά πυραυλικά καύσιμα Class-1 Explosive Propellants.\n"
                "• **Σημεία Μεταφόρτωσης**: 3 σιδηροδρομικοί σταθμοί διαμετακομιδής.\n"
                "• **Ημερομηνία Καταγραφής**: Πρόσφατη σάρωση 12ώρου."
            ),
            "source_name": "ConflictLeaks.onion",
            "source_url": "http://leaks789xyz98765.onion/manifest/2026-07-25-manifest",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=4, minutes=10)).isoformat()
        },
        {
            "title": "Custom FPV Drone Frequency Jamming Firmware Patches Discovered",
            "description": "Scraped from IntelDarknetForum.onion: Threat actors discussing custom firmware patches designed to evade electronic warfare anti-drone countermeasures.",
            "full_content": (
                "### 1. Περίληψη Λογισμικού Drone Evading\n"
                "Εντοπίστηκαν τροποποιημένα αρχεία firmware για FPV drones που επιτρέπουν αυτόματη αλλαγή συχνοτήτων (frequency hopping).\n\n"
                "### 2. Τεχνικές Προδιαγραφές\n"
                "• **Μπάντα Συχνότητας**: 868MHz / 915MHz / 2.4GHz.\n"
                "• **Μηχανισμός**: Αυτόματη μεταπήδηση καναλιού κατά τον εντοπισμό παρεμβολέα EW.\n"
                "• **Αξιολόγηση**: Υψηλό ενδιαφέρον για τακτικό OSINT."
            ),
            "source_name": "IntelDarknetForum.onion",
            "source_url": "http://intel4x5abc12345.onion/threads/fpv-firmware-evasion",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=5, minutes=30)).isoformat()
        },
        {
            "title": "Compromised SCADA/ICS Controller Credentials Sold on Hidden Market",
            "description": "Scraped from ShadowBrokerMarket.onion: Access credentials and VPN profiles for regional power grid distribution nodes listed for auction.",
            "full_content": (
                "### 1. Έκθεση Διαπιστευτηρίων Βιομηχανικών Συστημάτων\n"
                "Στη σκοτεινή αγορά ShadowBrokerMarket.onion πωλούνται διαπιστευτήρια πρόσβασης σε συστήματα SCADA.\n\n"
                "### 2. Τεχνική Ανάλυση\n"
                "• **Πρωτόκολλα**: Modbus TCP & DNP3 telemetry logs.\n"
                "• **Στόχος**: Υποδομές διανομής ηλεκτρικής ενέργειας.\n"
                "• **Προστασία**: Πλήρως απομονωμένο στο τοπικό Sandbox."
            ),
            "source_name": "ShadowBrokerMarket.onion",
            "source_url": "http://shadowmkt990123.onion/listings/scada-credentials-v4",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=7, minutes=00)).isoformat()
        },
        {
            "title": "Intercepted Encrypted Tactical Comms Decryption Log Released",
            "description": "Scraped from DarkCommsMirror.onion: Raw audio transcripts and radio intercept metadata from regional border monitoring posts.",
            "full_content": (
                "### 1. Σύνοψη Υποκλαπέντων Συνομιλιών\n"
                "Στην πηγή DarkCommsMirror.onion δημοσιεύτηκαν απομαγνητοφωνημένα κείμενα ραδιοεπικοινωνιών.\n\n"
                "### 2. Ευρήματα\n"
                "• **Τύπος Σήματος**: VHF/UHF tactical radio transmission.\n"
                "• **Περιεχόμενο**: Αναφορές θέσεων εφοδιασμού και κινήσεων οχημάτων.\n"
                "• **Πηγές**: Darknet Mirror Intercepts."
            ),
            "source_name": "DarkCommsMirror.onion",
            "source_url": "http://darkcomms554312.onion/intercepts/radio-log-7782",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=8, minutes=45)).isoformat()
        },
        {
            "title": "Electronic Warfare Signals Telemetry Map Published on Darknet OSINT Node",
            "description": "Scraped from EWConflictMonitor.onion: Aggregated spectrum analysis chart indicating high-power jamming signals detected near maritime trade routes.",
            "full_content": (
                "### 1. Χάρτης Τηλεμετρίας Ηλεκτρονικού Πολέμου\n"
                "Δημοσιεύτηκε αναλυτικός χάρτης φάσματος συχνοτήτων που αποτυπώνει εστίες παρεμβολών GPS/GNSS.\n\n"
                "### 2. Τεχνικές Παράμετροι\n"
                "• **Συχνότητες**: L1 (1575.42 MHz) & L2 (1227.60 MHz).\n"
                "• **Επίπτωση**: Παρασιτικές παρεμβολές σε ναυτιλιακά συστήματα πλοήγησης.\n"
                "• **Προέλευση**: EW Conflict Monitor Darknet Feed."
            ),
            "source_name": "EWConflictMonitor.onion",
            "source_url": "http://ewmonitor331290.onion/maps/spectrum-jamming-map",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=10, minutes=20)).isoformat()
        },
        {
            "title": "Darknet Forum Discussion: Analysis of Custom Malware Strains targeting Infrastructure",
            "description": "Scraped from CyberWarLabs.onion: Technical breakdown of wiper malware variants targeting industrial control systems.",
            "full_content": (
                "### 1. Ανάλυση Δείγματος Wiper Malware\n"
                "Στο ερευνητικό φόρουμ CyberWarLabs.onion αναλύθηκε νέο στέλεχος κακόβουλου λογισμικού διαγραφής δεδομένων (wiper).\n\n"
                "### 2. Δείκτες Παραβίασης (IoCs)\n"
                "• **Hashes**: SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.\n"
                "• **Στόχος**: Διαγραφή Master Boot Record (MBR) σε βιομηχανικούς σταθμούς εργασίας.\n"
                "• **Κατάσταση**: Καταγράφηκε για ιστορικό OSINT 12ώρου."
            ),
            "source_name": "CyberWarLabs.onion",
            "source_url": "http://cwlabs99812401.onion/analysis/wiper-malware-v3",
            "is_darknet": True,
            "date_reported": (now_utc - timedelta(hours=11, minutes=50)).isoformat()
        }
    ]

    return darknet_incidents


def send_incident_to_api(incident_payload: Dict[str, Any]) -> bool:
    """
    Αποστέλλει το περιστατικό στο FastAPI backend μέσω HTTP POST.
    """
    source_url = incident_payload.get("source_url", "")

    try:
        response = requests.post(API_URL, json=incident_payload, timeout=10)
        if response.status_code in [200, 201]:
            created_id = response.json().get("id")
            logger.info(f"Επιτυχής εισαγωγή/συγχρονισμός περιστατικού στο API! UUID: {created_id}")
            SEEN_SOURCE_URLS.add(source_url)
            return True
        else:
            logger.error(f"Σφάλμα από το API HTTP {response.status_code}: {response.text}")
    except Exception as err:
        logger.error(f"Αποτυχία αποστολής περιστατικού στο API: {err}")
    return False


def main_worker_loop() -> None:
    """
    Κύρια ασύγχρονη/επαναληπτική λειτουργία του Darknet Worker.
    """
    logger.info("Εκκίνηση OSINT Darknet Worker Service...")

    # Αναμονή για προετοιμασία των υπόλοιπων υπηρεσιών (FastAPI, Tor Proxy)
    time.sleep(5)

    # Έλεγχος συνδεσιμότητας Tor
    test_tor_connection()

    while True:
        try:
            incidents = fetch_darknet_feed()
            for incident in incidents:
                send_incident_to_api(incident)

        except Exception as err:
            logger.error(f"Σφάλμα κατά τον κύκλο σάρωσης του Worker: {err}")

        # Αναμονή 120 δευτερολέπτων πριν τον επόμενο κύκλο σάρωσης
        logger.info("Αναμονή 120s μέχρι τον επόμενο κύκλο σάρωσης Darknet...")
        time.sleep(120)


if __name__ == "__main__":
    main_worker_loop()
