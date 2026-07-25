from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# Ορισμός των 20 πιο αξιόπιστων πηγών OSINT που παρέχουν δωρεάν API keys
class OSINTProviderType(str, Enum):
    SHODAN = "shodan"
    VIRUSTOTAL = "virustotal"
    ALIENVAULT_OTX = "alienvault_otx"
    CENSYS = "censys"
    ABUSEIPDB = "abuseipdb"
    URLSCAN = "urlscan"
    SECURITYTRAILS = "securitytrails"
    GREYNOISE = "greynoise"
    HUNTER_IO = "hunter_io"
    HAVEIBEENPWNED = "haveibeenpwned"
    OPENSANCTIONS = "opensanctions"
    CRIMINAL_IP = "criminal_ip"
    IPINFO = "ipinfo"
    OPENSKY_NETWORK = "opensky_network"
    ACLED = "acled"
    LEAKIX = "leakix"
    BINARYEDGE = "binaryedge"
    HYBRID_ANALYSIS = "hybrid_analysis"
    ABSTRACT_API = "abstract_api"
    THREATFOX = "threatfox"
    CUSTOM = "custom"


# Πληροφορίες και μεταδεδομένα για κάθε υποστηριζόμενη πηγή OSINT
class ProviderMetadata(BaseModel):
    name: str = Field(..., description="Επίσημο όνομα της υπηρεσίας OSINT")
    category: str = Field(..., description="Κατηγορία συλλογής πληροφοριών")
    description: str = Field(..., description="Περιγραφή της υπηρεσίας")
    signup_url: str = Field(..., description="Σύνδεσμος εγγραφής για δωρεάν API Key")
    has_free_tier: bool = Field(default=True, description="Ένδειξη διαθεσιμότητας δωρεάν επιπέδου χρήσης")


# Λεξικό με τις λεπτομέρειες των 20 δημοφιλών OSINT resources
OSINT_PROVIDERS_REGISTRY: Dict[str, ProviderMetadata] = {
    OSINTProviderType.SHODAN.value: ProviderMetadata(
        name="Shodan",
        category="Network & Device Search",
        description="Μηχανή αναζήτησης για συσκευές συνδεδεμένες στο διαδίκτυο.",
        signup_url="https://account.shodan.io/register"
    ),
    OSINTProviderType.VIRUSTOTAL.value: ProviderMetadata(
        name="VirusTotal",
        category="Threat Intelligence & Malware",
        description="Ανάλυση αρχείων, τομέων και διευθύνσεων IP για απειλές.",
        signup_url="https://www.virustotal.com/gui/join-us"
    ),
    OSINTProviderType.ALIENVAULT_OTX.value: ProviderMetadata(
        name="AlienVault OTX",
        category="Threat Intelligence",
        description="Ανοιχτή κοινότητα ανταλλαγής πληροφοριών απειλών.",
        signup_url="https://otx.alienvault.com/"
    ),
    OSINTProviderType.CENSYS.value: ProviderMetadata(
        name="Censys",
        category="Attack Surface Management",
        description="Αναζήτηση εξυπηρετητών, πιστοποιητικών και υποδομών.",
        signup_url="https://censys.io/register"
    ),
    OSINTProviderType.ABUSEIPDB.value: ProviderMetadata(
        name="AbuseIPDB",
        category="IP Reputation",
        description="Κεντρική βάση δεδομένων ελέγχου και αναφοράς κακόβουλων IP.",
        signup_url="https://www.abuseipdb.com/register"
    ),
    OSINTProviderType.URLSCAN.value: ProviderMetadata(
        name="URLScan.io",
        category="Web Scanner & Sandbox",
        description="Σάρωση και ανάλυση ιστοσελίδων σε απομονωμένο περιβάλλον.",
        signup_url="https://urlscan.io/user/signup"
    ),
    OSINTProviderType.SECURITYTRAILS.value: ProviderMetadata(
        name="SecurityTrails",
        category="DNS & Domain Intelligence",
        description="Ιστορικά δεδομένα DNS, subdomains και WHOIS.",
        signup_url="https://securitytrails.com/app/signup"
    ),
    OSINTProviderType.GREYNOISE.value: ProviderMetadata(
        name="GreyNoise",
        category="Internet Noise Analysis",
        description="Φιλτράρισμα μαζικών σαρώσεων διαδικτύου και αναγνώριση επιθέσεων.",
        signup_url="https://viz.greynoise.io/signup"
    ),
    OSINTProviderType.HUNTER_IO.value: ProviderMetadata(
        name="Hunter.io",
        category="Email Intelligence",
        description="Αναζήτηση και επαλήθευση εταιρικών διευθύνσεων email.",
        signup_url="https://hunter.io/users/sign_up"
    ),
    OSINTProviderType.HAVEIBEENPWNED.value: ProviderMetadata(
        name="Have I Been Pwned",
        category="Data Breach Intelligence",
        description="Έλεγχος παραβιάσεων λογαριασμών και διαρροών διαπιστευτηρίων.",
        signup_url="https://haveibeenpwned.com/API/Key"
    ),
    OSINTProviderType.OPENSANCTIONS.value: ProviderMetadata(
        name="OpenSanctions",
        category="Sanctions & PEP Database",
        description="Ανοιχτή βάση δεδομένων κυρώσεων, πολιτικά εκτεθειμένων προσώπων.",
        signup_url="https://www.opensanctions.org/api/"
    ),
    OSINTProviderType.CRIMINAL_IP.value: ProviderMetadata(
        name="Criminal IP",
        category="Threat Intelligence & Asset Search",
        description="Μηχανή αναζήτησης απειλών στον κυβερνοχώρο και αξιολόγηση κινδύνου IP.",
        signup_url="https://www.criminalip.io/en/signup"
    ),
    OSINTProviderType.IPINFO.value: ProviderMetadata(
        name="IPinfo.io",
        category="IP Geolocation",
        description="Γεωεντοπισμός διευθύνσεων IP, ASN και δεδομένα δικτύου.",
        signup_url="https://ipinfo.io/signup"
    ),
    OSINTProviderType.OPENSKY_NETWORK.value: ProviderMetadata(
        name="OpenSky Network",
        category="Flight Tracking OSINT",
        description="Ανοιχτά δεδομένα παρακολούθησης πτήσεων και εναέριας κυκλοφορίας.",
        signup_url="https://opensky-network.org/community/registration"
    ),
    OSINTProviderType.ACLED.value: ProviderMetadata(
        name="ACLED",
        category="Armed Conflict Intelligence",
        description="Δεδομένα επεισοδίων ένοπλων συγκρούσεων και διαδηλώσεων παγκοσμίως.",
        signup_url="https://acleddata.com/data-export-tool/"
    ),
    OSINTProviderType.LEAKIX.value: ProviderMetadata(
        name="LeakIX",
        category="Exposed Services & Breaches",
        description="Ευρετήριο ανοιχτών υπηρεσιών και διαρροών δεδομένων στο διαδίκτυο.",
        signup_url="https://leakix.net/"
    ),
    OSINTProviderType.BINARYEDGE.value: ProviderMetadata(
        name="BinaryEdge",
        category="Threat Intelligence",
        description="Σάρωση και χαρτογράφηση επιφάνειας επιθέσεων στο διαδίκτυο.",
        signup_url="https://www.binaryedge.io/"
    ),
    OSINTProviderType.HYBRID_ANALYSIS.value: ProviderMetadata(
        name="Hybrid Analysis",
        category="Malware Sandbox",
        description="Δωρεάν υπηρεσία ανάλυσης κακόβουλου λογισμικού.",
        signup_url="https://www.hybrid-analysis.com/signup"
    ),
    OSINTProviderType.ABSTRACT_API.value: ProviderMetadata(
        name="Abstract API",
        category="IP & Web Intelligence",
        description="API γεωγραφικού εντοπισμού και επικύρωσης δεδομένων.",
        signup_url="https://www.abstractapi.com/"
    ),
    OSINTProviderType.THREATFOX.value: ProviderMetadata(
        name="ThreatFox",
        category="IOC Database",
        description="Βάση δεδομένων δεικτών συμβιβασμού (IOCs) από το abuse.ch.",
        signup_url="https://threatfox.abuse.ch/"
    )
}


def get_provider_info(provider_name: str) -> Optional[ProviderMetadata]:
    """
    Επιστρέφει τα μεταδεδομένα μιας πηγής OSINT βάσει του ονόματός της.
    
    Parameters:
        provider_name (str): Το όνομα της πηγής OSINT.
        
    Returns:
        Optional[ProviderMetadata]: Τα μεταδεδομένα αν βρεθούν, αλλιώς None.
    """
    return OSINT_PROVIDERS_REGISTRY.get(provider_name.lower())


def list_supported_providers() -> List[str]:
    """
    Επιστρέφει τη λίστα με όλες τις προ-ρυθμισμένες πηγές OSINT.
    
    Returns:
        List[str]: Λίστα ονομάτων πηγών OSINT.
    """
    return list(OSINT_PROVIDERS_REGISTRY.keys())
