import string
import requests
import json
import base64

class PFSenseData:
    server = None
    client_id = None
    client_key = None

    default_file = (
        'dev tun\n'+
        'persist-tun\n'+
        'persist-key\n'+
        'auth-nocache\n'+
        'cipher AES-256-CBC\n'+
        'data-ciphers AES-256-CBC\n'+
        'auth SHA256\n'+
        'tls-client\n'+
        'client\n'+
        'resolv-retry infinite\n'+
        'remote 96.82.37.3 1194 udp4\n'+
        'nobind\n'+
        'verify-x509-name "servercert" name\n'+
        'remote-cert-tls server\n'+
        'explicit-exit-notify\n'
    )

    @staticmethod
    def update_config(pf_config: dict) -> None:
        PFSenseData.server = pf_config.get('server')
        PFSenseData.client_id = pf_config.get('client-id')
        PFSenseData.client_key = pf_config.get('client-key')

    @staticmethod
    def format_name(input_string, replace_with="NA_"):
        ascii_friendly = ''.join(c if c in string.printable else replace_with for c in input_string)
        ascii_friendly = ''.join(c for c in ascii_friendly if c not in string.punctuation)
        ascii_friendly = ascii_friendly.replace(' ', '_')
        return ascii_friendly
    
    @staticmethod
    def create_config_file(cert, cert_auth):
        ca_cert = base64.b64decode(cert_auth.get('crt')).decode('utf-8')
        cli_cert = base64.b64decode(cert.get('crt')).decode('utf-8')
        key = base64.b64decode(cert.get('prv')).decode('utf-8')

        text = PFSenseData.default_file + (
            '\n\n'+
            f'<ca>\n{ca_cert}</ca>\n\n'+
            f'<cert>\n{cli_cert}</cert>\n\n'+
            f'<key>\n{key}</key>'
        )

        return text

    @staticmethod
    def export_vpn_profile(arcade: dict):
        if arcade is None:
            return None

        headers = {
            'Authorization': f'{PFSenseData.client_id} {PFSenseData.client_key}',
            'Content-Type': 'application/json'
        }
        arcade['name'] = PFSenseData.format_name(arcade['name'])

        def get_ca():
            try:
                response = requests.get(
                    f'{PFSenseData.server}/system/ca',
                    headers=headers,
                    verify=False,
                    timeout=10
                )

                response.raise_for_status()
                data = response.json().get('data')
                if data:
                    result = [item for item in data if item['descr'] == 'eamuse vpn']
                    if result:
                        return result[0]
                return None

            except requests.exceptions.RequestException as exception:
                print('An error occurred while making the request:', exception)
                return None

        def create_cert(cert_auth):
            certificate_data = {
                'method': 'internal',
                'descr': arcade['name'],
                'caref': cert_auth.get('refid'),
                'keytype': 'RSA',
                'keylen': 1024,
                'digest_alg': 'sha256',
                'lifetime': 3650,
                'dn_commonname': arcade['name'],
                'type': 'user',
                'dn_country': 'JP',
                'dn_state': 'Tokyo',
                'dn_city': 'Chuo City',
                'dn_organization': 'Konmai',
                'dn_organizationalunit': 'PhaseII'
            }

            try:
                response = requests.post(
                    f'{PFSenseData.server}/system/certificate',
                    headers=headers,
                    data=json.dumps(certificate_data),
                    verify=False,
                    timeout=10
                )

                response.raise_for_status()
                data = response.json().get('data')
                return data

            except requests.exceptions.RequestException as exception:
                print('An error occurred while making the request:', exception)

        def get_cert():
            try:
                response = requests.get(
                    f'{PFSenseData.server}/system/certificate',
                    headers=headers,
                    verify=False,
                    timeout=10
                )

                response.raise_for_status()
                data = response.json().get('data')
                if data:
                    result = [item for item in data if item['descr'] == arcade['name']]
                    if result:
                        return result[0], True
                    
                return None, False

            except requests.exceptions.RequestException as exception:
                print('An error occurred while making the request:', exception)
                return None, False

        ca = get_ca()
        if ca:
            (cert, already_exist) = get_cert()
            if not already_exist:
                cert = create_cert(ca)

            results = PFSenseData.create_config_file(cert, get_ca())
            generator = (cell for row in results
                            for cell in row)
            name = arcade['name'].replace(' ', '_')

            return (generator, name)
        
        return (None, None)