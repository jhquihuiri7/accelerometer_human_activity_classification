import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def gcs_client():
    from google.cloud import storage

    service_account_info = {
        "type": config['TYPE'],
        "project_id": config['PROJECT_ID'],
        "private_key_id": config['PRIVATE_KEY_ID'],
        "private_key": config['PRIVATE_KEY'],
        "client_email": config['CLIENT_EMAIL'],
        "client_id": config['CLIENT_ID'],
        "auth_uri": config['AUTH_URI'],
        "token_uri": config['TOKEN_URI'],
        "auth_provider_x509_cert_url": config['AUTH_PROVIDER_CERT_URL'],
        "client_x509_cert_url": config['CLIENT_CERT_URL']
    }
    #return storage.Client.from_service_account_info(service_account_info)
    #return storage.Client.from_service_account_json("./cardiocareai1-firebase-adminsdk-fbsvc-928b95aeb5.json")
    return storage.Client()