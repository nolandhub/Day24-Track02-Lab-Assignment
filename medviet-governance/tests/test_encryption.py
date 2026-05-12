# tests/test_encryption.py
import pytest
import base64
import pandas as pd
from src.encryption.vault import SimpleVault
import os
import json

class TestEncryptionVault:
    @pytest.fixture
    def vault(self):
        vault_path = ".vault_key_test"
        if os.path.exists(vault_path):
            os.remove(vault_path)
        return SimpleVault(master_key_path=vault_path)

    def test_kek_generated_on_first_run(self, vault):
        assert os.path.exists(".vault_key_test")
        assert len(vault.kek) == 32

    def test_encrypt_decrypt_roundtrip(self, vault):
        plaintext = "Bệnh nhân: Nguyễn Văn A - CCCD: 012345678901"
        encrypted = vault.encrypt_data(plaintext)
        decrypted = vault.decrypt_data(encrypted)
        assert decrypted == plaintext

    def test_different_ciphertexts_same_plaintext(self, vault):
        plaintext = "CCCD: 012345678901"
        encrypted1 = vault.encrypt_data(plaintext)
        encrypted2 = vault.encrypt_data(plaintext)
        assert encrypted1["ciphertext"] != encrypted2["ciphertext"]
        assert vault.decrypt_data(encrypted1) == plaintext
        assert vault.decrypt_data(encrypted2) == plaintext

class TestDataFrameEncryption:
    @pytest.fixture
    def vault(self):
        vault_path = ".vault_key_test"
        if os.path.exists(vault_path):
            os.remove(vault_path)
        return SimpleVault(master_key_path=vault_path)

    def test_encrypt_column(self, vault):
        df = pd.DataFrame({
            "patient_id": ["P001", "P002"],
            "cccd": ["012345678901", "098765432109"]
        })
        df_enc = vault.encrypt_column(df, "cccd")
        assert all(isinstance(x, str) for x in df_enc["cccd"])

    def test_decrypt_column_recovers_plaintext(self, vault):
        df = pd.DataFrame({
            "patient_id": ["P001", "P002"],
            "cccd": ["012345678901", "098765432109"]
        })
        original_cccd = df["cccd"].tolist()
        df_enc = vault.encrypt_column(df, "cccd")
        df_dec = vault.decrypt_column(df_enc, "cccd")
        assert df_dec["cccd"].tolist() == original_cccd
