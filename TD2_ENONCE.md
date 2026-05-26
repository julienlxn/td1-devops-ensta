# TD2 — Docker & Sécurité

**Durée :** 3h  
**Objectifs :** Conteneuriser une application, orchestrer plusieurs services, comprendre les enjeux de sécurité Docker

---

## Prérequis

- Docker Desktop installé (Windows/Mac) ou Docker Engine (Linux)
- VS Code avec l'extension Docker (recommandé)
- Le repo ENStartup cloné (TD1)
- Les credentials SSH fournis par l'instructeur (pour l'exercice 7)

---

## Exercice 1 : Premier Dockerfile (30 min) — 4 points

### Contexte

L'application ENStartup tourne sur votre machine, mais votre collègue n'arrive pas à la lancer — il manque des dépendances. Conteneurisez l'app pour que ça marche partout.

### Objectif

Écrivez un Dockerfile pour l'application Streamlit et faites-la tourner dans un container.

### Étapes

**1.1.** Créez un fichier `Dockerfile` à la racine du projet.

Voici les instructions dont vous aurez besoin (pas forcément dans cet ordre) :

| Instruction | Rôle |
|-------------|------|
| `FROM` | Image de base |
| `WORKDIR` | Répertoire de travail |
| `COPY` | Copier des fichiers |
| `RUN` | Exécuter une commande au build |
| `EXPOSE` | Documenter le port |
| `CMD` | Commande par défaut au lancement |

**Indices :**
- Image de base recommandée : `python:3.11-slim`
- Streamlit écoute sur le port `8501`
- Commande de lancement : `streamlit run app.py --server.address=0.0.0.0`
- Pensez à l'ordre des instructions pour optimiser le cache

**1.2.** Construisez l'image avec le tag `enstartup:v1`

**1.3.** Lancez un container en exposant le port 8501

**1.4.** Testez en ouvrant http://localhost:8501

### Questions

- Que se passe-t-il si vous modifiez `app.py` ? Pourquoi ?
  Le changement n'est pas visible. Le code est copié dans l'image au moment du build, il faut rebuilder pour que les modifications soient prises en compte.

- Comment arrêtez-vous le container ?
  docker stop [container_id] ou Ctrl+C si lancé en mode attaché.

- Quelle commande permet de voir les containers en cours d'exécution ?
  docker ps

### ✅ Checkpoint

- [ ] L'image est construite
- [ ] L'application est accessible sur http://localhost:8501

---

## Exercice 2 : Volumes (20 min) — 3 points

### Contexte

Modifier le code nécessite de rebuild l'image à chaque fois. En développement, c'est pénible.

### Objectif

Utilisez un volume pour voir les modifications en temps réel sans rebuild.

### Étapes

**2.1.** Relancez le container en montant le dossier courant dans `/app` du container.

**Indice :** L'option `-v` permet de monter un volume. La syntaxe est `-v <source>:<destination>`

**2.2.** Modifiez `app.py` (changez le titre par exemple) et rafraîchissez le navigateur.

### Questions

- Pourquoi le changement est-il visible sans rebuild ?
  > Le volume monte le dossier local directement dans le container. Docker lit les fichiers depuis le disque de la machine hôte en temps réel, pas depuis l'image.

- Si vous ajoutez une nouvelle dépendance dans `requirements.txt`, est-ce que le volume suffit ? Pourquoi ?
  > Non. Le volume partage les fichiers mais pas l'environnement Python. Les dépendances sont installées au moment du build, il faut donc rebuilder pour les prendre en compte.


### ✅ Checkpoint

- [ ] Les modifications de code sont visibles sans rebuild
- [ ] Vous comprenez la différence entre le code dans l'image et le volume

---

## Exercice 3 : Docker Compose avec Redis (35 min) — 4 points

### Contexte

Vous voulez ajouter un compteur de visites à l'application en utilisant Redis.

### Objectif

Créez un `docker-compose.yml` qui orchestre l'app Streamlit et Redis.

### Étapes

**3.1.** Créez un fichier `docker-compose.yml` avec deux services :
- `app` : votre application (construite depuis le Dockerfile)
- `redis` : l'image officielle `redis:alpine`

Consultez la documentation : https://docs.docker.com/compose/compose-file/

**3.2.** Ajoutez `redis` à vos dépendances Python.

**3.3.** Modifiez `app.py` pour vous connecter à Redis et incrémenter un compteur de visites.

```python
import redis
import os

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
visit_count = r.incr("visits")
```

Affichez `visit_count` quelque part dans l'interface.

**3.4.** Lancez les services et vérifiez que le compteur s'incrémente à chaque refresh.

### Debug

Si la connexion échoue, utilisez ces commandes pour investiguer :

```bash
docker compose logs <service>
docker compose exec <service> <commande>
```

### Questions

- Pourquoi utilisez-vous `redis` comme hostname et pas `localhost` ?
  > Dans Docker Compose, chaque service tourne dans son propre container. localhost désignerait le container lui-même. Docker Compose crée un réseau interne où chaque service est accessible via son nom de service, ici redis.

- Que fait `depends_on` ? Est-ce suffisant pour garantir que Redis est prêt ?
  > depends_on définit l'ordre de démarrage des services. Non, ce n'est pas suffisant : il garantit juste que le container Redis est lancé, pas qu'il est prêt à accepter des connexions.

- Comment vérifiez-vous que Redis répond depuis l'intérieur du container app ?
  > python -c "import redis; r = redis.Redis(host='redis'); print(r.ping())"


### ✅ Checkpoint

- [ ] Les deux services démarrent
- [ ] Le compteur de visites fonctionne

---

## Exercice 4 : Variables d'environnement (20 min) — 3 points

### Contexte

Les configurations sensibles ne doivent pas être en dur dans le code.

### Objectif

Externalisez la configuration dans un fichier `.env`.

### Étapes

**4.1.** Créez un fichier `.env` contenant :
- `REDIS_HOST`
- `REDIS_PORT`
- `APP_TITLE`
- `SECRET_API_KEY` (une valeur fictive)

**4.2.** Modifiez `docker-compose.yml` pour charger ce fichier.

**Indice :** Cherchez `env_file` dans la documentation Compose.

**4.3.** Modifiez `app.py` pour utiliser `APP_TITLE` dans le titre de la page.

**4.4.** Inspectez le container et cherchez vos variables d'environnement.

```bash
docker inspect <container_id>
```

### Questions

- Où voyez-vous vos variables dans la sortie de `docker inspect` ?
  > Dans la section "Env" sous "Config".

- Pourquoi est-ce un problème de sécurité ?
  > Les variables sont visibles en clair par quiconque a accès au daemon Docker, y compris les secrets comme SECRET_API_KEY.

- Que devez-vous ajouter au `.gitignore` ?
  > Le fichier .env pour ne pas pousser les secrets sur GitHub.

- En production, quelle serait une meilleure solution ?
  > Utiliser un gestionnaire de secrets comme Azure Key Vault ou AWS Secrets Manager.


### ✅ Checkpoint

- [ ] L'application utilise les variables depuis `.env`
- [ ] Vous comprenez les risques de sécurité

---

## Exercice 5 : Debug & Monitoring (25 min) — 3 points

### Contexte

En production, il faut savoir débugger et monitorer les containers.

### Objectif

Maîtrisez les commandes de debug Docker.

### Étapes

**5.1.** Lancez les services en mode détaché (background).

**5.2.** Explorez ces commandes et notez ce qu'elles font :

```bash
docker compose logs -f
docker compose exec <service> bash
docker stats
docker inspect <container>
```

**5.3.** Depuis l'intérieur du container `app`, vérifiez :
- La version de Python
- Les variables d'environnement
- Si vous pouvez pinguer `redis`

**5.4.** Ajoutez des healthchecks à vos services dans `docker-compose.yml`.

**Indice :** Cherchez "healthcheck" dans la documentation Compose. Pour Redis, `redis-cli ping` renvoie `PONG` si Redis est prêt.

### Questions

- Quelle est la différence entre `docker logs` et `docker compose logs` ?
  > docker logs cible un seul container par son ID. docker compose logs affiche les logs de tous les services du compose en même temps avec le nom du service devant chaque ligne.

- À quoi sert un healthcheck ?
  > À vérifier automatiquement qu'un service est prêt et fonctionnel, pas juste démarré. Docker peut ainsi attendre qu'un service soit healthy avant de démarrer les services qui en dépendent.

- Comment `depends_on` peut-il utiliser les healthchecks ?
  > Avec condition: service_healthy, le service app ne démarre que quand redis est marqué healthy par son healthcheck.

### ✅ Checkpoint

- [ ] Vous savez suivre les logs, entrer dans un container, monitorer les ressources
- [ ] Les healthchecks sont configurés

---

## Exercice 6 : Multi-stage Build (20 min) — 3 points

### Contexte

Votre image fait 400-500 Mo. En production, on veut des images minimales.

### Objectif

Optimisez la taille de l'image avec un multi-stage build.

### Étapes

**6.1.** Notez la taille actuelle de votre image.

**6.2.** Créez un nouveau fichier `Dockerfile.optimized` avec deux stages :
- **Stage 1 (builder)** : installez les dépendances dans un virtualenv
- **Stage 2 (runtime)** : copiez seulement le virtualenv depuis le builder

**Indices :**
- `FROM ... AS builder` pour nommer un stage
- `COPY --from=builder /source /dest` pour copier depuis un stage précédent
- Créez un virtualenv avec `python -m venv /opt/venv`

**6.3.** Ajoutez un utilisateur non-root et utilisez-le avec l'instruction `USER`.

**6.4.** Construisez et comparez les tailles.

### Questions

- Quel gain de taille avez-vous obtenu ?
  > Taille initiale : 837 Mo → Taille optimisée : 858 Mo. Pas de gain significatif ici car Streamlit et ses dépendances sont volumineuses dans les deux cas. Le multi-stage build est plus utile pour des apps avec des dépendances de compilation.

- Pourquoi utiliser un utilisateur non-root ?
  > Si un attaquant exploite une faille dans l'app, il se retrouve avec les droits d'un utilisateur limité et non root, ce qui limite les dégâts sur le système.

- Que se passe-t-il si vous essayez d'écrire dans un dossier appartenant à root ?
  > Permission denied, l'utilisateur non-root n'a pas les droits d'écriture dans les dossiers root.

### ✅ Checkpoint

- [ ] L'image optimisée est plus petite
- [ ] Elle utilise un utilisateur non-root

---

## Exercice 7 : CTF — Exploit du groupe Docker (25 min) — 4 points

### ⚠️ Contexte

Vous êtes un pentester. On vous a donné un accès SSH à un serveur avec un compte utilisateur limité. Cet utilisateur est membre du groupe `docker`.

**Votre mission : lisez le fichier `/root/flag.txt` sans être root.**

### Connexion

```bash
ssh prenom@4.233.139.22
# Mot de passe : PRENOMprenom00@
```

### Étapes

**7.1.** Vérifiez vos droits actuels. Pouvez-vous lire `/root/flag.txt` ?

> **Résultat de la commande :**

**7.2.** Vérifiez vos groupes. Que remarquez-vous ?

> **Groupes de votre utilisateur :**

**7.3.** Trouvez un moyen d'exploiter votre appartenance au groupe `docker` pour accéder aux fichiers root.

**Indice :** Avec Docker, vous pouvez monter n'importe quel dossier de l'hôte dans un container...

> **Commande docker utilisée pour accéder à `/root/flag.txt` :**
> ```
>
> ```
>
> **Contenu de `/root/flag.txt` :**

**7.4.** Scannez (avec `find -f` les fichiers qui pourraient être intéressants pour un acteur malveillant : `.env`, par exemple)
Vous pouvez aussi scanner tous les fichiers du systeme, et filtrer avec `grep` des choses comme `API_KEY` et l'extraire

> **Valeur de l'`API_KEY` trouvée :**

**7.5.** (Bonus) Pouvez-vous obtenir un shell root sur l'hôte ? Prouvez le en créant un fichier `PWNED_BY_prenom.txt` sur le `/home` de l'utilisateur`adminensta`

> **Commande utilisée pour obtenir un shell root :**
> ```
>
> ```

### Questions

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

### ✅ Checkpoint

- [ ] Vous avez récupéré le `API_KEY`
- [ ] Vous pouvez expliquer l'exploit

---

## Exercice 8 : Remédiation avec Podman (15 min) — 2 points

### Contexte

Docker pose un problème de sécurité avec son daemon root. Podman est une alternative "rootless".

### Objectif

Testez Podman et comparez avec Docker.

### Étapes

**8.1.** Vérifiez que Podman est installé sur la VM.

**8.2.** Tentez le même exploit qu'avec Docker, mais avec Podman.

**8.3.** Comparez les résultats.

### Questions

- Pourquoi l'exploit ne fonctionne-t-il pas avec Podman ?
  > Podman est rootless : les containers tournent avec l'UID de l'utilisateur courant, pas root. Monter / dans le container ne donne donc pas accès aux fichiers root.

- Différences architecturales entre Docker et Podman ?
  > Docker utilise un daemon central qui tourne en root, ce qui donne des privilèges élevés à tous les utilisateurs du groupe docker. Podman n'a pas de daemon, chaque container tourne directement avec les droits de l'utilisateur qui le lance.

- Dans quel contexte recommander Podman plutôt que Docker ?
  > En entreprise sur des serveurs partagés où la sécurité est prioritaire, ou quand on ne veut pas donner de droits root implicites aux développeurs.


### ✅ Checkpoint

- [ ] L'exploit ne fonctionne pas avec Podman
- [ ] Vous comprenez pourquoi

---

## Barème

| Exercice | Points |
|----------|--------|
| 1. Dockerfile | 4 |
| 2. Volumes | 3 |
| 3. Compose + Redis | 4 |
| 4. Variables d'env | 3 |
| 5. Debug & Monitoring | 3 |
| 6. Multi-stage build | 3 |
| 7. CTF Sécurité | 4 |
| 8. Podman | 2 |
| **Total** | **26** |

---

## Ressources

- [Documentation Docker](https://docs.docker.com/)
- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Compose file reference](https://docs.docker.com/compose/compose-file/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Podman](https://podman.io/)
