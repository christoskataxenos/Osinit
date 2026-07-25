import os
import base64
import secrets
from typing import Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Κλάση διαχείρισης κρυπτογράφησης και ασφαλούς αποθήκευσης των API Keys
class KeyVault:
    """
    Διαχειρίζεται την κρυπτογράφηση και αποκρυπτογράφηση ευαίσθητων API keys
    χρησιμοποιώντας τον αλγόριθμο Fernet (συμμετρική κρυπτογράφηση).
    """

    def __init__(self, master_secret: Optional[str] = None):
        """
        Αρχικοποίηση του μηχανισμού κρυπτογράφησης με κύριο μυστικό κλειδί.
        
        Parameters:
            master_secret (Optional[str]): Κύριο μυστικό. Αν δεν δοθεί, λαμβάνεται από το περιβάλλον.
        """
        # Λήψη μυστικού κλειδιού από τις μεταβλητές περιβάλλοντος
        secret_key = master_secret or os.getenv("SECRET_ENCRYPTION_KEY", "osinit_default_secret_key_32_bytes_len!")
        
        # Παραγωγή Fernet key μέσω PBKDF2HMAC για μέγιστη ασφάλεια
        salt = b"osinit_key_vault_salt_static"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode("utf-8")))
        self._cipher = Fernet(derived_key)

    def encrypt_key(self, raw_api_key: str) -> str:
        """
        Κρυπτογραφεί ένα API key σε μορφή κωδικοποιημένου string.
        
        Parameters:
            raw_api_key (str): Το απλό, ανεπεξέργαστο API key.
            
        Returns:
            str: Το κρυπτογραφημένο API key.
        """
        encrypted_bytes = self._cipher.encrypt(raw_api_key.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt_key(self, encrypted_api_key: str) -> str:
        """
        Αποκρυπτογραφεί ένα κρυπτογραφημένο API key.
        
        Parameters:
            encrypted_api_key (str): Το κρυπτογραφημένο string.
            
        Returns:
            str: Το αρχικό API key.
        """
        decrypted_bytes = self._cipher.decrypt(encrypted_api_key.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    @staticmethod
    def generate_random_api_key(prefix: str = "osinit_key") -> str:
        """
        Δημιουργεί ένα νέο τυχαίο εσωτερικό API key για επικοινωνία μεταξύ συστημάτων.
        
        Parameters:
            prefix (str): Πρόθεμα για το αναγνωριστικό του κλειδιού.
            
        Returns:
            str: Παραγόμενο ασφαλές API key.
        """
        random_token = secrets.token_hex(24)
        return f"{prefix}_{random_token}"

    @staticmethod
    def mask_api_key(raw_api_key: str) -> str:
        """
        Επιστρέφει μια συγκαλυμμένη μορφή του API key για ασφαλή προβολή.
        
        Parameters:
            raw_api_key (str): Το πλήρες API key.
            
        Returns:
            str: Το συγκαλυμμένο API key (π.χ. 'abcd...xyz1').
        """
        if len(raw_api_key) <= 8:
            return "****"
        return f"{raw_api_key[:4]}...{raw_api_key[-4:]}"
