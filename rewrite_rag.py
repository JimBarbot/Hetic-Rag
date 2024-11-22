import torch
import ollama
import os
from openai import OpenAI
import argparse

# Codes d'échappement ANSI pour les couleurs
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Fonction pour ouvrir un fichier et retourner son contenu sous forme de chaîne de caractères
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Fonction pour obtenir le contexte pertinent du coffre en fonction de l'entrée de l'utilisateur
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Vérifie si le tenseur a des éléments
        return []
    # Encode l'entrée réécrite
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    # Calcule la similarité cosinus entre l'entrée et les embeddings du coffre
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    # Ajuste top_k si c'est plus grand que le nombre d'éléments disponibles
    top_k = min(top_k, len(cos_scores))
    # Trie les scores et obtient les indices des top-k
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    # Obtient le contexte correspondant du coffre
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

# Fonction pour interagir avec le modèle Ollama
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    # Obtient le contexte pertinent du coffre
    relevant_context = get_relevant_context(user_input, vault_embeddings_tensor, vault_content, top_k=3)
    if relevant_context:
        # Convertit la liste en une seule chaîne avec des sauts de ligne entre les éléments
        context_str = "\n".join(relevant_context)
        print("Contexte extrait des documents : \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "Aucun contexte pertinent trouvé." + RESET_COLOR)
    
    # Prépare l'entrée de l'utilisateur en la concaténant avec le contexte pertinent
    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = context_str + "\n\n" + user_input
    
    # Ajoute l'entrée de l'utilisateur à l'historique de la conversation
    conversation_history.append({"role": "user", "content": user_input_with_context})
    
    # Crée un historique des messages incluant le message système et l'historique de la conversation
    messages = [
        {"role": "system", "content": system_message},
        *conversation_history
    ]
    
    # Envoie la demande de complétion au modèle Ollama
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages
    )
    
    # Ajoute la réponse du modèle à l'historique de la conversation
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    # Retourne le contenu de la réponse du modèle
    return response.choices[0].message.content

# Analyse des arguments en ligne de commande
parser = argparse.ArgumentParser(description="Chat Ollama")
parser.add_argument("--model", default="dolphin-llama3", help="Modèle Ollama à utiliser (par défaut : llama3)")
args = parser.parse_args()

# Configuration du client API Ollama
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='dolphin-llama3'
)

# Chargement du contenu du coffre
vault_content = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

# Génère les embeddings pour le contenu du coffre à l'aide d'Ollama
vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
    vault_embeddings.append(response["embedding"])

# Conversion en tenseur et affichage des embeddings
vault_embeddings_tensor = torch.tensor(vault_embeddings) 
print("Embeddings pour chaque ligne du coffre :")
print(vault_embeddings_tensor)

# Boucle de conversation
conversation_history = []
system_message = "Vous êtes un assistant utile et expert dans l'extraction des informations les plus pertinentes d'un texte donné"

while True:
    user_input = input(YELLOW + "Posez une question sur vos documents (ou tapez 'quit' pour quitter) : " + RESET_COLOR)
    if user_input.lower() == 'quit':
        break

    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
    print(NEON_GREEN + "Réponse : \n\n" + response + RESET_COLOR)
