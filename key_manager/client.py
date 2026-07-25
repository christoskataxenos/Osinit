import os
import httpx
from typing import Optional, Dict, List, Any


# Κλάση client για εύκολη επικοινωνία του main backend και των workers με το Key Manager subproject
class OSINTKeyClient:
    """
    Client επικοινωνίας για την άντληση αποκρυπτογραφημένων OSINT API keys
    από το υποσύστημα key_manager.
    """

    def __init__(self, key_manager_base_url: Optional[str] = None):
        """
        Αρχικοποίηση του OSINTKeyClient.
        
        Parameters:
            key_manager_base_url (Optional[str]): Η διεύθυνση URL της υπηρεσίας key_manager.
        """
        self.base_url = key_manager_base_url or os.getenv(
            "KEY_MANAGER_URL",
            "http://key-manager:8002"
        ).rstrip("/")

    async def get_api_key(self, provider_name: str) -> Optional[str]:
        """
        Ανακτά το ενεργό αποκρυπτογραφημένο API key για μια πηγή OSINT.
        
        Parameters:
            provider_name (str): Το όνομα της πηγής OSINT (π.χ. 'shodan', 'acled').
            
        Returns:
            Optional[str]: Το αλφαριθμητικό του API key ή None αν δεν βρεθεί.
        """
        url = f"{self.base_url}/api/v1/keys/{provider_name.lower().strip()}/decrypted"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("api_key_value")
                return None
        except Exception:
            # Επιστροφή None σε περίπτωση αποτυχίας σύνδεσης
            return None

    async def register_key(self, provider_name: str, key_name: str, api_key_value: str) -> Optional[Dict[str, Any]]:
        """
        Καταχωρεί ένα νέο API key στο subproject key_manager.
        
        Parameters:
            provider_name (str): Όνομα της πηγής OSINT.
            key_name (str): Περιγραφή του κλειδιού.
            api_key_value (str): Η τιμή του API key.
            
        Returns:
            Optional[Dict[str, Any]]: Τα επιστρεφόμενα στοιχεία από το API.
        """
        url = f"{self.base_url}/api/v1/keys"
        payload = {
            "provider_name": provider_name,
            "key_name": key_name,
            "api_key_value": api_key_value
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 201:
                    return response.json()
                return None
        except Exception:
            return None

    async def list_available_providers(self) -> Dict[str, Any]:
        """
        Επιστρέφει τη λίστα με τις υποστηριζόμενες OSINT πηγές.
        
        Returns:
            Dict[str, Any]: Λεξικό με τις διαθέσιμες πηγές.
        """
        url = f"{self.base_url}/api/v1/providers"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                return {}
        except Exception:
            return {}
