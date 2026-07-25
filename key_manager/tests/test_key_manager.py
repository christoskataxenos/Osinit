import sys
import os
import pytest
from fastapi.testclient import TestClient

# Προσθήκη του φακέλου key_manager στο sys.path για εισαγωγή των modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from key_vault import KeyVault
from osint_providers import list_supported_providers, get_provider_info


def test_key_vault_encryption_decryption() -> None:
    """
    Unit Test: Έλεγχος ότι η κρυπτογράφηση και η αποκρυπτογράφηση λειτουργούν σωστά.
    """
    # Δημιουργία δοκιμαστικού KeyVault
    vault = KeyVault(master_secret="test_secret_key_1234567890123456")
    original_key = "shodan_secret_api_key_xyz_123"

    # Κρυπτογράφηση του κλειδιού
    encrypted = vault.encrypt_key(original_key)
    assert encrypted != original_key

    # Αποκρυπτογράφηση του κλειδιού
    decrypted = vault.decrypt_key(encrypted)
    assert decrypted == original_key

    # Έλεγχος της συγκάλυψης (masking)
    masked = vault.mask_api_key(original_key)
    assert masked.startswith("shod")
    assert masked.endswith("_123")


def test_osint_providers_registry() -> None:
    """
    Unit Test: Έλεγχος ότι οι 20 προ-ρυθμισμένες πηγές OSINT είναι διαθέσιμες.
    """
    providers = list_supported_providers()
    assert len(providers) >= 20
    assert "shodan" in providers
    assert "virustotal" in providers
    assert "acled" in providers

    # Έλεγχος μεταδεδομένων
    shodan_info = get_provider_info("shodan")
    assert shodan_info is not None
    assert shodan_info.name == "Shodan"
    assert "signup_url" in shodan_info.model_dump()


def test_invalid_key_decryption_edge_case() -> None:
    """
    Edge Case Test: Έλεγχος αποτυχίας αποκρυπτογράφησης με άκυρο/παραποιημένο κρυπτογραφημένο string.
    """
    vault = KeyVault(master_secret="test_secret_key_1234567890123456")
    invalid_encrypted_str = "invalid_cipher_text_format"

    with pytest.raises(Exception):
        vault.decrypt_key(invalid_encrypted_str)
