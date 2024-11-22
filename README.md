
### Configuration pour lancer le projet sur votre machine, j'ai fais exactement comme votre premier exemple en cours

1 - Ouvrir votre terminal 
2 - Faites un git clone + url 
3 - Aller à l'emplacement du dossier
4 - Entrée cette commande dans le terminal : pip install -r configuration.txt
5 - Si cela n'est pas fait, il faut installer Ollama : https://ollama.com/download 
6 - Dans le terminal faite cela : ollama pull llama3 
7 - Ensuite, importer un fichier pdf avec cette commande : python pdf_dl.py
8 - Inserer la commande : python local_rag.py 
9 - Poser votre question en anglais de préférence, en suite vous aurez le document puis la réponse de l'IA en verte concernant votre question. 

### Les questions, c'est préférable en anglais car la version françaisen j'ai tester et c'est pas très bon en termes. 

### Ensuite j'ai voulu aller plus loin avec la connexion avec google cloud drive. 

- Dans le terminal : pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

- Ensuite dans le terminal faites : python test_gdrive.py 

- Vous devrez avoir une page Google qui s'ouvre. Cependant, je dois ajouter un utilisateur dans Google Console Cloud pour que ça marche donc faute de temps et de solution j'ai pris la mienne. De votre coté je doute que ça marche mais je vais mettre dans le projet des screen montrant que je peux me connecter au drive. 