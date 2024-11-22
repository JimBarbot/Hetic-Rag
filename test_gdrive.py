import os
import pickle
from urllib.request import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Si vous modifiez les étendues, supprimez le fichier token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_gdrive():
    creds = None
    # Le fichier token.pickle stocke les informations d'accès et d'actualisation de l'utilisateur.
    # Il est créé automatiquement lorsque le flux d'authentification est terminé pour la première fois.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si les informations d'identification sont invalides ou expirées, redemander l'authentification.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Enregistrer les informations d'identification pour la prochaine fois.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def list_drive_files():
    try:
        # Authentification et accès à l'API Google Drive
        service = authenticate_gdrive()

        # Appel à l'API pour lister les fichiers
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('Aucun fichier trouvé.')
        else:
            print('Fichiers dans votre Google Drive:')
            for item in items:
                print(f"{item['name']} (ID: {item['id']})")
    except HttpError as error:
        print(f"Une erreur est survenue: {error}")

# Exécuter la fonction pour lister les fichiers
list_drive_files()
