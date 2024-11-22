# Lire les URLs depuis un fichier texte
def read_urls_from_txt(file_path):
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f.readlines()]
    return urls

# Exemple d'utilisation
url_file = "urls.txt"
shared_drive_files = read_urls_from_txt(url_file)

print("Liste des URLs :")
for url in shared_drive_files:
    print(url)
