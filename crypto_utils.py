"""
Crypto Utils - Funciones criptográficas OFFLINE para generación de wallets
Sin conexión a internet, usando solo librerías locales
"""

import os
import base58
import hashlib
import qrcode
from io import BytesIO
from mnemonic import Mnemonic
from bip32 import BIP32
from PIL import Image

# Bitcoin
from bit import Key as BitcoinKey

# Ethereum
from eth_account import Account
import coincurve


def generate_mnemonic(strength_bits=256):
    """
    Genera un mnemonic BIP39 aleatorio usando os.urandom (100% offline)
    
    Args:
        strength_bits: 128, 160, 192, 224, o 256 bits (default: 256 = 24 palabras)
    
    Returns:
        str: Mnemonic de 12, 15, 18, 21 o 24 palabras según strength_bits
    """
    mnemo = Mnemonic("english")
    entropy = os.urandom(strength_bits // 8)
    mnemonic = mnemo.to_mnemonic(entropy)
    return mnemonic


def mnemonic_to_seed(mnemonic, passphrase=""):
    """
    Convierte mnemonic BIP39 a seed (usando PBKDF2 - offline)
    
    Args:
        mnemonic: La frase mnemonic
        passphrase: Passphrase opcional (default: "")
    
    Returns:
        bytes: Seed de 64 bytes
    """
    mnemo = Mnemonic("english")
    seed = mnemo.to_seed(mnemonic, passphrase=passphrase)
    return seed


def derive_btc_keys(mnemonic, passphrase="", testnet=False):
    """
    Deriva claves Bitcoin usando BIP32/BIP44 (offline)
    
    Args:
        mnemonic: La frase mnemonic
        passphrase: Passphrase opcional
        testnet: True para red testnet, False para mainnet
    
    Returns:
        dict: {'private_key_hex': str, 'private_key_wif': str, 'address': str}
    """
    seed = mnemonic_to_seed(mnemonic, passphrase)
    bip32 = BIP32.from_seed(seed)
    
    # BIP44 path: m/44'/0'/0'/0/0 (Bitcoin)
    # testnet: m/44'/1'/0'/0/0
    coin_type = 1 if testnet else 0
    derivation_path = f"m/44'/{coin_type}'/0'/0/0"
    
    # Deriva las claves
    xprv = bip32.get_xpriv_from_path(derivation_path)
    private_bytes = bytes.fromhex(xprv.hex())
    
    # Usar `bit` para generar la dirección (offline)
    if testnet:
        from bit import PrivateKeyTestnet as KeyClass
    else:
        from bit import PrivateKey as KeyClass
    
    key = KeyClass.from_hex(private_bytes.hex())
    
    return {
        'private_key_hex': key.to_hex(),
        'private_key_wif': key.to_wif(),
        'address': key.address
    }


def derive_eth_keys(mnemonic, passphrase=""):
    """
    Deriva claves Ethereum usando BIP44 (offline)
    
    Args:
        mnemonic: La frase mnemonic
        passphrase: Passphrase opcional
    
    Returns:
        dict: {'private_key_hex': str, 'address': str}
    """
    seed = mnemonic_to_seed(mnemonic, passphrase)
    bip32 = BIP32.from_seed(seed)
    
    # BIP44 path para Ethereum: m/44'/60'/0'/0/0
    derivation_path = "m/44'/60'/0'/0/0"
    
    # Deriva clave privada
    derived_private_key = bip32.get_privkey_from_path(derivation_path)
    
    # Crear cuenta Ethereum (offline)
    account = Account.from_key(derived_private_key.hex())
    
    return {
        'private_key_hex': derived_private_key.hex(),
        'address': account.address
    }


def generate_qr_code(data, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4):
    """
    Genera un QR code desde datos (offline)
    
    Args:
        data: String a codificar en QR
        error_correction: Nivel de corrección de errores
        box_size: Tamaño de cada caja
        border: Border
    
    Returns:
        PIL.Image: Imagen del QR code
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def generate_qr_base64(data, size=10):
    """
    Genera un QR code y lo convierte a base64 para incrustar en HTML (offline)
    
    Args:
        data: String a codificar
        size: Tamaño del QR
    
    Returns:
        str: Data URI con imagen PNG en base64
    """
    img = generate_qr_code(data, box_size=size)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def save_qr_image(data, filepath, size=10):
    """
    Guarda un QR code como archivo PNG (offline)
    
    Args:
        data: String a codificar
        filepath: Ruta del archivo de salida
        size: Tamaño del QR
    """
    img = generate_qr_code(data, box_size=size)
    img.save(filepath)


def validate_cryptocurrency(coin):
    """
    Valida que la criptomoneda sea soportada
    
    Args:
        coin: String con el nombre de la moneda
    
    Returns:
        bool: True si es válida
    
    Raises:
        ValueError: Si la moneda no es soportada
    """
    supported = {'btc', 'eth', 'bitcoin', 'ethereum'}
    coin_lower = coin.lower().strip()
    if coin_lower not in supported:
        raise ValueError(f"Criptomoneda no soportada: {coin}. Usa: btc, eth, bitcoin, ethereum")
    return True
