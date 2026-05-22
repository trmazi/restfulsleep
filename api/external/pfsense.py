import string
import requests
import json

class PFSense:
    server = None
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
        'remote 23.162.224.238 1194 udp4\n' +
        'nobind\n'+
        'verify-x509-name "servercert" name\n'+
        'remote-cert-tls server\n'+
        'explicit-exit-notify\n'
    )

    @staticmethod
    def updateConfig(pf_config: dict) -> None: 
        PFSense.server = pf_config.get('server')
        PFSense.client_key = pf_config.get('client-key')

    @staticmethod
    def format_name(input_string, replace_with="NA_"):
        ascii_friendly = ''.join(c if c in string.printable else replace_with for c in input_string)
        ascii_friendly = ''.join(c for c in ascii_friendly if c not in string.punctuation)
        ascii_friendly = ascii_friendly.replace(' ', '_')
        return ascii_friendly
    
    @staticmethod
    def create_config_file(cert, cert_auth):
        ca_cert = cert_auth.get('crt')
        cli_cert = cert.get('crt')
        key = cert.get('prv')

        text = PFSense.default_file + (
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
            'X-API-Key': PFSense.client_key,
            'Content-Type': 'application/json'
        }
        arcade['name'] = PFSense.format_name(arcade['name'])

        def get_ca():
            try:
                response = requests.get(
                    f'{PFSense.server}/system/certificate_authorities',
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
                'keylen': 2048,
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
                    f'{PFSense.server}/system/certificate/generate',
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

        def get_certs():
            try:
                response = requests.get(
                    f'{PFSense.server}/system/certificates',
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
            (cert, already_exist) = get_certs()
            if not already_exist:
                cert = create_cert(ca)

            results = PFSense.create_config_file(cert, ca)
            generator = (cell for row in results
                            for cell in row)
            name = arcade['name'].replace(' ', '_')

            return (generator, name)
        
        return (None, None)