# import io
import requests

def upload(file):
    with requests.Session() as rs:
        server = rs.get('https://api.gofile.io/getServer').json()['data']['server']
        with open(file, 'rb') as f:
            uploaded = rs.post(f'https://{server}.gofile.io/uploadFile', files={'file':f}).json()

            if uploaded['status'] == 'ok':
                return {
                        'status': uploaded['status'],
                        'filename': uploaded['data']['fileName'],
                        'dl_page': uploaded['data']['downloadPage'],
                        'direct_dl': uploaded['data']['directLink']
                        }
            return uploaded
