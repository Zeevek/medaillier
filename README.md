<p align="center"><img src="logo.svg" width="120" alt="Logo Challenges Pharmacie"></p>

# Challenges Pharmacie

Tableau de bord **100 % hors-ligne** pour suivre les challenges laboratoires d'une officine : objectifs, rythme de vente, rémunérations, rapport PDF et répartition des gains à l'équipe.

**Un seul fichier HTML, aucune installation, aucune donnée envoyée sur internet.**

## 🚀 Démarrage

1. Téléchargez `index.html` (ou clonez ce dépôt).
2. Ouvrez le fichier dans votre navigateur (double-clic).
3. C'est tout — les données sont enregistrées automatiquement dans le navigateur (localStorage).

> 💡 Astuce : ajoutez la page aux favoris ou créez un raccourci sur le bureau du poste de l'officine.

## ✨ Fonctionnalités

### 📊 Suivi des challenges
- Fiches par laboratoire : cible, période, objectif, réalisé
- **Saisie mensuelle** alignée sur le logiciel métier (LGO), total et projection automatiques
- Indicateur de **rythme** (dans les temps / en retard) et projection de fin de période
- Mode comptoir : boutons **+1 / +5** pour incrémenter à la volée
- Bandeau de suivi des mises à jour hebdomadaires, écart depuis la dernière saisie
- Historique, tendance (sparkline), bascule de période
- Logos des laboratoires : import local, glisser-déposer, coller (Ctrl+V), bibliothèque réutilisable

### 💶 Rémunérations
Trois modes par challenge :
- **€ par boîte** : tranches marginales, booster (tranche à tarif majoré), minimum optionnel conditionnant le paiement
- **Par produit** : boîtes vendues × barème par produit (1 €/boîte par défaut si non détaillé)
- **Paliers** : primes cumulatives par seuil
- **Gains acquis** (au réalisé actuel) et **gains estimés** (à la projection de fin de période), avec estimation du montant débloqué par le franchissement du minimum

### 📄 Rapport PDF
- Page de synthèse : indicateurs clés, podium, classement, gains totaux
- Une fiche par challenge avec jauge de progression
- Génération PDF intégrée (bascule automatique sur l'impression navigateur hors-ligne)

### 💰 Répartition des gains
- Sélection des challenges à répartir (montants pré-remplis, laboratoires ajoutables à la main)
- Équipe : nom, prénom, email, poste (pharmacien, préparateur, rayonniste, étudiant)
- Pondération par **coefficient de poste** et, en option, par **heures travaillées** (référentiel temps plein paramétrable, ex. 10 h / 35 h)
- Case « Participe » pour inclure/exclure une personne d'une distribution sans la retirer de l'effectif
- Totaux : à verser, déjà versé, reste à verser — impression et export CSV dédiés

### 🔒 Données & portabilité
- Tout est stocké **localement** dans le navigateur ; rien ne quitte le poste
- **Sauvegarde / chargement `.json`** (challenges, historique, logos, répartition) pour transférer d'un poste à l'autre
- **Export CSV** (tableur) avec neutralisation de l'injection de formule

## 📖 Aide intégrée

Le bouton **ⓘ Aide** dans l'application détaille chaque fonction, et **✨ Nouveautés** affiche le journal des versions.

## 🛠️ Technique

- Un seul fichier : HTML + CSS + JavaScript vanilla, aucune dépendance à installer
- Persistance : `localStorage`
- Fonctionne hors-ligne (la génération PDF utilise une librairie CDN si disponible, sinon l'impression du navigateur)
- Testé sur les navigateurs modernes (Chrome, Edge, Firefox)
- **Interface adaptée au mobile** : utilisable sur smartphone et tablette (aperçu du rapport mis à l'échelle, tableaux défilables)

## 📜 Licence

[MIT](LICENSE) — utilisation, modification et partage libres.
