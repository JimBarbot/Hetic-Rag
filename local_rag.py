import torch
import ollama
import os
from openai import OpenAI
import argparse
import json





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

# Fonction pour reformuler la requête de l'utilisateur en utilisant l'historique de la conversation
def rewrite_query(user_input_json, conversation_history, ollama_model):
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
    prompt = f"""Reformulez la requête suivante en incorporant le contexte pertinent de l'historique de la conversation.
    La requête reformulée doit :
    
    - Préserver l'intention et la signification de base de la requête originale
    - Développer et clarifier la requête pour la rendre plus spécifique et informative afin d'extraire le contexte pertinent
    - Éviter d'introduire de nouveaux sujets ou requêtes qui s'écartent de la requête originale
    - NE PAS RÉPONDRE à la requête originale, mais au contraire vous concentrer sur sa reformulation et son expansion en une nouvelle requête
    
    Retournez UNIQUEMENT la requête reformulée, sans aucun autre formatage ou explication.
    
    Historique de la conversation :
    {context}
    
    Requête originale : [{user_input}]
    
    Requête reformulée : 
    """
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})
   
# Fonction pour interagir avec le modèle Ollama et générer la réponse
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    
    if len(conversation_history) > 1:
        query_json = {
            "Query": user_input,
            "Rewritten Query": ""
        }
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, ollama_model)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
        print(PINK + "Requête originale : " + user_input + RESET_COLOR)
        print(PINK + "Requête reformulée : " + rewritten_query + RESET_COLOR)
    else:
        rewritten_query = user_input
    
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Contexte extrait des documents : \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "Aucun contexte pertinent trouvé." + RESET_COLOR)
    
    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = user_input + "\n\nContexte pertinent :\n" + context_str
    
    conversation_history[-1]["content"] = user_input_with_context
    
    messages = [
        {"role": "system", "content": system_message},
        *conversation_history
    ]
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )
    
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    return response.choices[0].message.content

# Analyse des arguments en ligne de commande
print(NEON_GREEN + "Analyse des argument en ligne de commande..." + RESET_COLOR)
parser = argparse.ArgumentParser(description="Chat Ollama")
parser.add_argument("--model", default="llama3", help="Modèle Ollama à utiliser (par défaut : llama3)")
args = parser.parse_args()

# Configuration du client API Ollama
print(NEON_GREEN + "Initialisation du client API Ollama..." + RESET_COLOR)
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)

# Chargement du contenu du coffre
print(NEON_GREEN + "Chargement du contenu du coffre..." + RESET_COLOR)
vault_content = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

# Génère les embeddings pour le contenu du coffre à l'aide d'Ollama
print(NEON_GREEN + "Génération des embeddings pour le contenu du coffre..." + RESET_COLOR)
vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
    vault_embeddings.append(response["embedding"])

# Conversion en tenseur et affichage des embeddings
print("Conversion des embeddings en tenseur...")
vault_embeddings_tensor = torch.tensor(vault_embeddings) 
print("Embeddings pour chaque ligne du coffre :")
print(vault_embeddings_tensor)

# Boucle de conversation
print("Démarrage de la boucle de conversation...")
conversation_history = []
system_message = "Vous êtes un assistant utile. Apportez également des informations supplémentaires pertinentes à la requête de l'utilisateur en dehors du contexte donné."

while True:
    user_input = input(YELLOW + "Posez une question sur le document (ou tapez 'quit' pour quitter) : " + RESET_COLOR)
    if user_input.lower() == 'quit':
        break
    
    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
    print(NEON_GREEN + "Réponse : \n\n" + response + RESET_COLOR)
