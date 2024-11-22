import os
import pickle
from urllib.request import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_gdrive():
    creds = None
    # Vérifiez si le fichier token.pickle existe déjà
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si les informations d'authentification ne sont pas valides, redemandez à l'utilisateur de se connecter
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # Le chemin vers votre fichier credentials.json
            creds = flow.run_local_server(port=0)
        
        # Enregistrez les informations d'authentification pour les futures utilisations
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

# Exemple d'appel pour l'authentification
service = authenticate_gdrive()

# Vous pouvez ensuite utiliser 'service' pour accéder aux fichiers de Google Drive
