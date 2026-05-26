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