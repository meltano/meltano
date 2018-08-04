import os

config = {
    'connection': {
        'username': os.getenv('SFDC_USERNAME'),
        'password': os.getenv('FIXED_SFDC_PASSWORD') or os.getenv('SFDC_PASSWORD'),
        'security_token': os.getenv('SFDC_SECURITY_TOKEN'),
    },
    'threads': int(os.getenv('SFDC_THREADS', 1)),
}

def manifest_file_path(args):
    return os.path.join(os.path.dirname(__file__), "..", "sfdc_manifest.yaml")
