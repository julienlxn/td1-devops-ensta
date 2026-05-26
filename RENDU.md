# Rendu TD1 - Julien

## Exercice 1
- Pourquoi crée-t-on une branche plutôt que de committer directement sur main ? 
Pour travailler de notre côté, tester des trucs et autre sans perturber le code principal.

## Exercice 2 - Capture The Bug

### Bug 1
- Déclencheur : Supprimer tous les éléments filtrés.
- Commit fautif : 002ad360
- Auteur : Serpico
- Ligne problématique : avg = total // count
- Correction appliquée : avg = total // count if count > 0 else 0. Si count vaut 0 on évite la division par zéro.

### Bug 2
- Déclencheur : Taper un ou plusieurs caractères spéciaux en barre de recherche.
- Commit fautif : e9b5614e
- Auteur : Serpico
- Ligne problématique : data[data["product"].str.contains(search)]
- Correction appliquée : ajout de regex=False et na=False dans str.contains. Par défaut pandas interprète la recherche comme une regex, ce qui fait crasher des caractères comme * ou (.

### Bug 3
- Déclencheur : Mettre un numéro de ligne dans la sidebar supérieur au nombre de résultats affichés après filtrage.
- Commit fautif : 7abdaeda
- Auteur : Serpico
- Ligne problématique : row_index = st.sidebar.number_input("Numéro de ligne", min_value=1, max_value=100, value=1)
- Correction appliquée : remplacé max_value=100 par max_value=max(0, len(filtered)-1) pour que le max s'adapte aux données affichées. Ajout d'une garde len(filtered) > 0 avant le iloc pour éviter le crash sur liste vide.

## Exercice 3
- Commit de résolution : 9a2317b
- Qu'est-ce qu'un conflit Git et pourquoi survient-il ? Un conflit survient quand deux branches ont modifié les mêmes lignes d'un même fichier et qu'on tente de les fusionner. Git ne sait pas quelle version garder et demande une résolution manuelle.
- (Bonus) Différence entre merge et rebase : merge crée un commit de fusion en préservant l'historique des deux branches, rebase réécrit les commits par-dessus la branche cible pour avoir un historique linéaire.


## Exercice 4
- Commande utilisée pour squasher les 3 commits : git reset --soft HEAD~3 puis git commit -m "Fix: correction des 3 bugs"
- Pourquoi squasher avant de merger ? Pour avoir un historique propre sur main avec un seul commit logique plutôt que 3 commits intermédiaires.
- Différence entre `--soft`, `--mixed` et `--hard` : --soft annule les commits mais garde les fichiers stagés ; --mixed annule les commits et déstage les fichiers mais garde les modifs dans le code ; --hard annule tout et supprime définitivement les modifications.
- Hash du commit hotfix sur main : 76ae0aa
- Pourquoi cherry-picker vers dev plutôt que merger main dans dev ? dev contient des features en cours non prêtes pour la prod, on ne veut pas les embarquer avec le fix.

## Exercices 5/6
- Lien vers le workflow GitHub Actions : https://github.com/julienlxn/td1-devops-ensta/actions
- Qu'apporte la CI par rapport à des tests lancés manuellement ? Les tests tournent automatiquement à chaque push sans qu'on y pense, ce qui détecte les régressions immédiatement.
- Pourquoi filtrer les fichiers qui déclenchent la CI ? Pour ne pas lancer des tests inutilement sur des changements non fonctionnels comme le readme.

# Rendu TD2 

## Exercice 1 : Premier Dockerfile (30 min) — 4 points

- Que se passe-t-il si vous modifiez `app.py` ? Pourquoi ?
  Le changement n'est pas visible. Le code est copié dans l'image au moment du build, il faut rebuilder pour que les modifications soient prises en compte.

- Comment arrêtez-vous le container ?
  docker stop [container_id] ou Ctrl+C si lancé en mode attaché.

- Quelle commande permet de voir les containers en cours d'exécution ?
  docker ps

## Exercice 2 : Volumes (20 min) — 3 points

- Pourquoi le changement est-il visible sans rebuild ?
  > Le volume monte le dossier local directement dans le container. Docker lit les fichiers depuis le disque de la machine hôte en temps réel, pas depuis l'image.

- Si vous ajoutez une nouvelle dépendance dans `requirements.txt`, est-ce que le volume suffit ? Pourquoi ?
  > Non. Le volume partage les fichiers mais pas l'environnement Python. Les dépendances sont installées au moment du build, il faut donc rebuilder pour les prendre en compte.

## Exercice 3 : Docker Compose avec Redis (35 min) — 4 points


- Pourquoi utilisez-vous `redis` comme hostname et pas `localhost` ?
  > Dans Docker Compose, chaque service tourne dans son propre container. localhost désignerait le container lui-même. Docker Compose crée un réseau interne où chaque service est accessible via son nom de service, ici redis.

- Que fait `depends_on` ? Est-ce suffisant pour garantir que Redis est prêt ?
  > depends_on définit l'ordre de démarrage des services. Non, ce n'est pas suffisant : il garantit juste que le container Redis est lancé, pas qu'il est prêt à accepter des connexions.

- Comment vérifiez-vous que Redis répond depuis l'intérieur du container app ?
  > python -c "import redis; r = redis.Redis(host='redis'); print(r.ping())"


## Exercice 4 : Variables d'environnement (20 min) — 3 points


- Où voyez-vous vos variables dans la sortie de `docker inspect` ?
  > Dans la section "Env" sous "Config".

- Pourquoi est-ce un problème de sécurité ?
  > Les variables sont visibles en clair par quiconque a accès au daemon Docker, y compris les secrets comme SECRET_API_KEY.

- Que devez-vous ajouter au `.gitignore` ?
  > Le fichier .env pour ne pas pousser les secrets sur GitHub.

- En production, quelle serait une meilleure solution ?
  > Utiliser un gestionnaire de secrets comme Azure Key Vault ou AWS Secrets Manager.

## Exercice 5 : Debug & Monitoring (25 min) — 3 points

- Quelle est la différence entre `docker logs` et `docker compose logs` ?
  > docker logs cible un seul container par son ID. docker compose logs affiche les logs de tous les services du compose en même temps avec le nom du service devant chaque ligne.

- À quoi sert un healthcheck ?
  > À vérifier automatiquement qu'un service est prêt et fonctionnel, pas juste démarré. Docker peut ainsi attendre qu'un service soit healthy avant de démarrer les services qui en dépendent.

- Comment `depends_on` peut-il utiliser les healthchecks ?
  > Avec condition: service_healthy, le service app ne démarre que quand redis est marqué healthy par son healthcheck.


## Exercice 6 : Multi-stage Build (20 min) — 3 points

- Quel gain de taille avez-vous obtenu ?
  > Taille initiale : 837 Mo → Taille optimisée : 858 Mo. Pas de gain significatif ici car Streamlit et ses dépendances sont volumineuses dans les deux cas. Le multi-stage build est plus utile pour des apps avec des dépendances de compilation.

- Pourquoi utiliser un utilisateur non-root ?
  > Si un attaquant exploite une faille dans l'app, il se retrouve avec les droits d'un utilisateur limité et non root, ce qui limite les dégâts sur le système.

- Que se passe-t-il si vous essayez d'écrire dans un dossier appartenant à root ?
  > Permission denied, l'utilisateur non-root n'a pas les droits d'écriture dans les dossiers root.


## Exercice 7 : CTF — Exploit du groupe Docker (25 min) — 4 points

- Résultat cat /root/flag.txt : Permission denied
- Groupes : julien docker
- Commande docker utilisée : docker run -v /:/mnt --rm -it alpine cat /mnt/root/flag.txt
- Contenu de /root/flag.txt : FLAG=3
- Api key trouvée :9q8O16xcDI1CCGoO2y29

- Pourquoi cette faille existe-t-elle ?
  > Le daemon Docker tourne en root. Un utilisateur membre du groupe docker peut monter n'importe quel dossier de l'hôte dans un container, y compris /, ce qui donne accès à tout le système de fichiers avec les droits root.

- Expliquez l'exploit à un manager non-technique :
  > On a utilisé Docker pour créer un mini-système qui a accès à tous les fichiers du serveur. Comme Docker tourne avec les droits administrateur, on a pu lire des fichiers normalement protégés, comme si on avait le mot de passe root.

- Comment sécuriser l'accès à Docker en entreprise ?
  > Ne pas mettre les utilisateurs dans le groupe docker. Utiliser Podman qui est rootless, ou configurer des politiques d'accès strictes via sudo.


## Exercice 8 : Remédiation avec Podman (15 min) — 2 points

### Questions

- Pourquoi l'exploit ne fonctionne-t-il pas avec Podman ?
  > Podman est rootless : les containers tournent avec l'UID de l'utilisateur courant, pas root. Monter / dans le container ne donne donc pas accès aux fichiers root.

- Différences architecturales entre Docker et Podman ?
  > Docker utilise un daemon central qui tourne en root, ce qui donne des privilèges élevés à tous les utilisateurs du groupe docker. Podman n'a pas de daemon, chaque container tourne directement avec les droits de l'utilisateur qui le lance.

- Dans quel contexte recommander Podman plutôt que Docker ?
  > En entreprise sur des serveurs partagés où la sécurité est prioritaire, ou quand on ne veut pas donner de droits root implicites aux développeurs.
