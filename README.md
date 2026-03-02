# Paper Wallet Generator

Generador **100% offline** de paper wallets para Bitcoin y Ethereum.

## ⚠️ Advertencia de Seguridad

**Este software genera claves privadas reales.** Úsalo solo en un entorno seguro y offline.

- Nunca compartas tu clave privada ni tu frase de recuperación (mnemonic)
- Guarda los paper wallets en un lugar físicamente seguro
- Para mainnet: prueba exhaustivamente en testnet primero

## 🚀 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

## 📋 Uso

### Bitcoin (Testnet - para pruebas)
```bash
python3 generate.py --coin btc --output btc_wallet.html --testnet --show-mnemonic
```

### Ethereum (Mainnet)
```bash
python3 generate.py --coin eth --output eth_wallet.html --show-mnemonic
```

### Parámetros
- `--coin`: `btc` o `eth`
- `--output`: Ruta del archivo HTML generado
- `--testnet`: Usar testnet (solo BTC)
- `--show-mnemonic`: Incluir la frase de recuperación

## 🏗️ Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `generate.py` | Script principal CLI |
| `crypto_utils.py` | Funciones criptográficas (BIP39/BIP32/BIP44) |
| `wallet_template.html` | Template HTML para el paper wallet |
| `requirements.txt` | Dependencias Python |

## 🔐 Características

- ✅ **100% Offline**: Sin conexión a internet
- ✅ **BIP39**: Mnemonics de 12-24 palabras
- ✅ **BIP44**: Derivation path estándar
- ✅ **QR Codes**: Direcciones y claves privadas escaneables
- ✅ **HTML Imprimible**: Diseño limpio tipo paper wallet tradicional

## 🧪 Testimonios

Genera un wallet de testnet para verificar:

```bash
python3 generate.py --coin btc --output test.html --testnet --show-mnemonic
```

## 📄 Licencia

MIT - Usar bajo tu propia responsabilidad.
