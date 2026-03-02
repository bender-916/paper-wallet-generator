#!/usr/bin/env python3
"""
Paper Wallet Generator CLI
Genera paper wallets offline para Bitcoin y Ethereum
"""

import argparse
import os
import sys
from datetime import datetime

# Importar funciones criptográficas
from crypto_utils import (
    generate_mnemonic,
    derive_btc_keys,
    derive_eth_keys,
    generate_qr_base64,
    validate_cryptocurrency
)


def parse_arguments():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Generate secure paper wallets for Bitcoin and Ethereum (100% offline)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate Bitcoin testnet wallet
  python generate.py --coin btc --output my_btc_wallet.html --testnet
  
  # Generate Ethereum mainnet wallet with mnemonic backup
  python generate.py --coin eth --output my_eth_wallet.html --show-mnemonic
  
  # Generate Bitcoin mainnet wallet
  python generate.py --coin btc --output btc_wallet.html
        '''
    )
    
    parser.add_argument(
        '--coin',
        required=True,
        choices=['btc', 'eth', 'bitcoin', 'ethereum'],
        help='Cryptocurrency type (btc/bitcoin or eth/ethereum)'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Output file path for the generated HTML wallet'
    )
    
    parser.add_argument(
        '--testnet',
        action='store_true',
        help='Use testnet instead of mainnet (for testing only)'
    )
    
    parser.add_argument(
        '--show-mnemonic',
        action='store_true',
        help='Include mnemonic phrase in the wallet and save to separate .txt file'
    )
    
    return parser.parse_args()


def load_template(template_path=None):
    """Carga el template HTML"""
    if template_path is None:
        # Usar template por defecto en el mismo directorio
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, 'wallet_template.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_wallet(coin, output_path, testnet=False, show_mnemonic=False):
    """
    Genera una paper wallet completa
    
    Args:
        coin: 'btc' o 'eth'
        output_path: Ruta del archivo HTML de salida
        testnet: True para usar testnet
        show_mnemonic: True para incluir mnemonic en el wallet
    """
    print(f"🔐 Generating {coin.upper()} paper wallet...")
    print(f"   Network: {'Testnet' if testnet else 'Mainnet'}")
    
    # Step 1: Generar mnemonic BIP39
    print("   📝 Generating BIP39 mnemonic...")
    mnemonic = generate_mnemonic(strength_bits=256)
    
    # Step 2: Derivar claves según la moneda
    print("   🔑 Deriving keys...")
    coin_lower = coin.lower().strip()
    
    if coin_lower in ['btc', 'bitcoin']:
        keys = derive_btc_keys(mnemonic, passphrase="", testnet=testnet)
        coin_name = 'Bitcoin' if not testnet else 'Bitcoin Testnet'
    elif coin_lower in ['eth', 'ethereum']:
        if testnet:
            print("   ℹ️  Ethereum testnet uses the same addresses as mainnet")
        keys = derive_eth_keys(mnemonic, passphrase="")
        coin_name = 'Ethereum'
    else:
        raise ValueError(f"Unsupported cryptocurrency: {coin}")
    
    address = keys['address']
    private_key = keys.get('private_key_wif', keys.get('private_key_hex'))
    
    print(f"   ✅ Address: {address[:20]}...{address[-10:]}")
    
    # Step 3: Generar QRs base64
    print("   📱 Generating QR codes...")
    address_qr = generate_qr_base64(address, size=10)
    private_key_qr = generate_qr_base64(private_key, size=10)
    
    # Step 4: Cargar y rellenar template
    print("   🎨 Creating wallet HTML...")
    template_content = load_template()
    
    # Preparar datos para el template
    template_data = {
        'COIN': coin_name,
        'ADDRESS': address,
        'ADDRESS_QR': address_qr,
        'PRIVATE_KEY': private_key,
        'PRIVATE_KEY_QR': private_key_qr,
        'DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
    }
    
    # Manejar el mnemonic de forma segura (sin Jinja2)
    if show_mnemonic:
        # Escapar el mnemonic para HTML
        mnemonic_escaped = mnemonic.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        mnemonic_html = f'''
            <div class="mnemonic-section">
                <div class="info-label">🔑 Recovery Phrase (Mnemonic)</div>
                <div class="mnemonic-words">{mnemonic_escaped}</div>
            </div>'''
        template_data['MNEMONIC'] = mnemonic_html
    else:
        template_data['MNEMONIC'] = '<!-- Mnemonic not included for security -->'
    
    # Reemplazar placeholders manualmente
    html_content = template_content
    for key, value in template_data.items():
        placeholder = f'{{{{{key}}}}}'
        html_content = html_content.replace(placeholder, value)
    
    # Limpiar la sintaxis de template de Jinja si quedó
    html_content = html_content.replace('{% if MNEMONIC %}', '')
    html_content = html_content.replace('{% endif %}', '')
    
    # Step 5: Guardar HTML
    print(f"   💾 Saving wallet to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Step 6: Opcionalmente guardar mnemonic en archivo separado
    if show_mnemonic:
        mnemonic_path = output_path.replace('.html', '_mnemonic.txt')
        print(f"   📝 Saving mnemonic backup to: {mnemonic_path}")
        with open(mnemonic_path, 'w', encoding='utf-8') as f:
            f.write(f"{coin_name} Paper Wallet - Mnemonic Backup\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"Address: {address}\n")
            f.write("-" * 50 + "\n")
            f.write(f"{mnemonic}\n")
            f.write("-" * 50 + "\n")
            f.write("\n⚠️  WARNING: Keep this file secret and secure!\n")
            f.write("Anyone with this mnemonic can access your funds.\n")
    
    print("\n✅ Paper wallet generated successfully!")
    print(f"\n📋 Summary:")
    print(f"   Coin: {coin_name}")
    print(f"   Address: {address}")
    print(f"   Output: {output_path}")
    if show_mnemonic:
        print(f"   Mnemonic: {mnemonic_path}")
    
    return True


def main():
    """Función principal"""
    try:
        args = parse_arguments()
        
        # Validar criptomoneda
        validate_cryptocurrency(args.coin)
        
        # Verificar que el directorio de salida existe
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Generar wallet
        success = generate_wallet(
            coin=args.coin,
            output_path=args.output,
            testnet=args.testnet,
            show_mnemonic=args.show_mnemonic
        )
        
        if success:
            print("\n⚠️  IMPORTANT SECURITY REMINDERS:")
            print("   • Store the HTML file in a secure, offline location")
            print("   • Never share your private key or mnemonic with anyone")
            print("   • Consider printing the wallet and storing it in a safe")
            print("   • For mainnet use: Test thoroughly on testnet first!")
            return 0
        else:
            return 1
            
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"\n❌ Error: Template file not found - {e}", file=sys.stderr)
