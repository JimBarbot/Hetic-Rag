import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re
import json

# Fonction pour convertir un PDF en texte et l'ajouter à vault.txt
def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers PDF", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "
            
            # Normaliser les espaces blancs et nettoyer le texte
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Diviser le texte en morceaux par phrases, en respectant une taille de morceau maximale
            sentences = re.split(r'(?<=[.!?]) +', text)  # diviser sur les espaces suivant la ponctuation de fin de phrase
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Vérifier si la phrase actuelle plus le morceau actuel dépasse la limite
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 pour l'espace
                    current_chunk += (sentence + " ").strip()
                else:
                    # Lorsque le morceau dépasse 1000 caractères, le stocker et commencer un nouveau morceau
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Ne pas oublier le dernier morceau !
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Écrire chaque morceau sur sa propre ligne
                    vault_file.write(chunk.strip() + "\n")  # Deux sauts de ligne pour séparer les morceaux
            print(f"Le contenu du PDF a été ajouté à vault.txt avec chaque morceau sur une ligne séparée.")

# Fonction pour télécharger un fichier texte et l'ajouter à vault.txt
def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
            
            # Normaliser les espaces blancs et nettoyer le texte
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Diviser le texte en morceaux par phrases, en respectant une taille de morceau maximale
            sentences = re.split(r'(?<=[.!?]) +', text)  # diviser sur les espaces suivant la ponctuation de fin de phrase
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Vérifier si la phrase actuelle plus le morceau actuel dépasse la limite
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 pour l'espace
                    current_chunk += (sentence + " ").strip()
                else:
                    # Lorsque le morceau dépasse 1000 caractères, le stocker et commencer un nouveau morceau
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Ne pas oublier le dernier morceau !
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Écrire chaque morceau sur sa propre ligne
                    vault_file.write(chunk.strip() + "\n")  # Deux sauts de ligne pour séparer les morceaux
            print(f"Le contenu du fichier texte a été ajouté à vault.txt avec chaque morceau sur une ligne séparée.")

# Fonction pour télécharger un fichier JSON et l'ajouter à vault.txt
def upload_jsonfile():
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            
            # Aplatir les données JSON en une seule chaîne de caractères
            text = json.dumps(data, ensure_ascii=False)
            
            # Normaliser les espaces blancs et nettoyer le texte
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Diviser le texte en morceaux par phrases, en respectant une taille de morceau maximale
            sentences = re.split(r'(?<=[.!?]) +', text)  # diviser sur les espaces suivant la ponctuation de fin de phrase
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Vérifier si la phrase actuelle plus le morceau actuel dépasse la limite
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 pour l'espace
                    current_chunk += (sentence + " ").strip()
                else:
                    # Lorsque le morceau dépasse 1000 caractères, le stocker et commencer un nouveau morceau
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Ne pas oublier le dernier morceau !
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Écrire chaque morceau sur sa propre ligne
                    vault_file.write(chunk.strip() + "\n")  # Deux sauts de ligne pour séparer les morceaux
            print(f"Le contenu du fichier JSON a été ajouté à vault.txt avec chaque morceau sur une ligne séparée.")

# Créer la fenêtre principale
root = tk.Tk()
root.title("Télécharger .pdf, .txt ou .json")

# Créer un bouton pour ouvrir la boîte de dialogue de fichier pour le PDF
pdf_button = tk.Button(root, text="Télécharger PDF", command=convert_pdf_to_text)
pdf_button.pack(pady=10)

# Créer un bouton pour ouvrir la boîte de dialogue de fichier pour le fichier texte
txt_button = tk.Button(root, text="Télécharger fichier texte", command=upload_txtfile)
txt_button.pack(pady=10)

# Créer un bouton pour ouvrir la boîte de dialogue de fichier pour le fichier JSON
json_button = tk.Button(root, text="Télécharger fichier JSON", command=upload_jsonfile)
json_button.pack(pady=10)

# Exécuter la boucle principale des événements
root.mainloop()
