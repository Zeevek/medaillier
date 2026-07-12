# Le Médaillier — architecture du dépôt

© 2026 Kévin François Cagnat

## Le problème

Un catalogue numismatique complet, c'est potentiellement **des centaines de milliers de
fiches**. Une base monolithique (`base-donnees.json`) est téléchargée *et gardée en
mémoire en entier* à chaque ouverture : au-delà de quelques milliers de pièces, l'app
devient inutilisable sur téléphone.

Ordres de grandeur mesurés sur les données réelles :

| Volume | Index allégé | Fiches complètes |
|---|---|---|
| 7 000 (zone euro) | 0,8 Mo | 4,3 Mo |
| 50 000 (+ monde) | 5,9 Mo | 31 Mo |
| 200 000 | 24 Mo | 123 Mo |
| 500 000 | 59 Mo | 308 Mo |

## La solution : trois niveaux

Une fiche complète pèse ~620 octets, mais **118 octets suffisent** pour chercher,
lister, filtrer et détecter les séries. D'où la séparation :

```
1. manifest.json      1 Ko     toujours chargé      → quels catalogues existent
2. index.json         ~120 o/pièce, par module      → chercher / lister / filtrer
3. f/NNN.json         ~620 o/pièce, par paquet      → détail, chargé à la demande
```

Au démarrage, l'app télécharge **le manifeste + l'index des modules activés**. Rien de
plus. Le détail d'une pièce n'est téléchargé qu'à l'ouverture de sa fiche, par paquets
de 400, puis conservé hors-ligne dans IndexedDB.

Conséquence : quelqu'un qui ne collectionne que les 2 € circulantes télécharge
**0,13 Mo**, même si le dépôt en héberge 500 000.

## Arborescence

```
medaillier/                        ← racine publiée (GitHub Pages)
├── index.html                     ← l'application
├── sw.js                          ← service worker (cache v10)
├── manifest.webmanifest
├── icon-192.png, icon-512.png, apple-touch-icon.png
├── series-donnees.json            ← base des SÉRIES de collection
├── LICENSE, README.md, ARCHITECTURE.md
│
├── data/                          ← LE CATALOGUE
│   ├── manifest.json              ← registre des modules
│   └── modules/
│       ├── euro-circulantes/
│       │   ├── index.json         ← 855 fiches allégées (0,13 Mo)
│       │   └── f/
│       │       ├── 000.json       ← fiches 1-400, complètes
│       │       ├── 001.json
│       │       └── 002.json
│       └── euro-collection/
│           ├── index.json         ← 6 024 fiches allégées (1,03 Mo)
│           └── f/000.json … 015.json
│
├── sources/                       ← données brutes d'entrée (non publiées)
│   └── catalogue-zone-euro-COMPLET.json
└── outils/
    └── construire-catalogue.py    ← régénère data/ depuis sources/
```

## Ajouter un catalogue

1. Déposer le JSON brut des pièces dans `sources/`.
2. Ajouter une entrée dans `MODULES` (fichier `outils/construire-catalogue.py`) :

```python
{
    "id": "france-francs",
    "libelle": "France — francs (1795-2001)",
    "description": "Francs, nouveaux francs, anciens francs.",
    "source": "france-francs.json",
    "filtre": lambda p: True,
    "defaut": False,
},
```

3. Lancer `python3 outils/construire-catalogue.py`.
4. Committer `data/`.

L'app proposera le nouveau catalogue automatiquement, sans qu'une ligne de code de
l'application ne change.

## Modules suggérés

| Module | Contenu | Volume estimé |
|---|---|---|
| `euro-circulantes` | cents, 1 €, 2 € — **fait** | 855 |
| `euro-collection` | or, argent, BE/BU — **fait** | 6 024 |
| `france-francs` | francs, anciens francs, Ve/IVe/IIIe Rép. | ~3 000 |
| `france-royales` | royales, féodales, révolutionnaires | ~10 000 |
| `monde-circulantes` | pièces courantes hors zone euro | ~30 000 |
| `antiques` | grecques, romaines, byzantines | ~50 000 |

Découper par **zone géographique ou par époque**, jamais par pays : un manifeste de
200 lignes serait illisible.

## Limites à connaître

- **GitHub** : 100 Mo par fichier (bloquant), ~1 Go par dépôt recommandé. Les paquets
  de 400 fiches pèsent ~250 Ko : très en dessous. Un module de 200 000 pièces =
  500 fichiers de paquets, ce qui reste raisonnable.
- **GitHub Pages** : 1 Go de site, 100 Go/mois de bande passante. Confortable.
- **Mémoire du navigateur** : l'index d'un module actif est gardé en RAM. Au-delà de
  ~50 000 pièces *par module actif*, prévoir de découper davantage.
- **Images** : jamais copiées, seulement liées (URL Numista). Le dépôt reste léger.

## Format des fiches

### Fiche allégée (`index.json`) — clés courtes

| clé | sens |
|---|---|
| `i` | identifiant Numista |
| `n` | nom |
| `p` | pays |
| `a` | année |
| `f` | valeur faciale |
| `c` | catégorie |
| `k` | numéro KM |
| `v` | chemin de la vignette (URL reconstruite via `baseImages`) |
| `b` | numéro du paquet contenant la fiche complète |

### Fiche complète (`f/NNN.json`)

Tous les champs : poids, diamètre, métal, tirage, tranches, ateliers, inscriptions,
graveur, notes, images avers/revers, lien Numista…

## Catégories (taxonomie Numista)

Pièce courante · Pièce circulante commémorative · Pièce non circulante ·
Pièce pour collectionneurs · Monnaie de siège · Monnaie de nécessité officielle ·
Jeton de marchand · Pièce locale · Essai · Fausse monnaie d'époque · Proto-monnaie

Si le champ `categorie` est absent, l'app la déduit du nom.

## Note sur les données Numista

Le catalogue Numista est le fruit du travail de milliers de contributeurs et fait
l'objet de conditions d'utilisation. Recopier l'intégralité de leur base dans un dépôt
**public** sous licence propriétaire est juridiquement discutable.

Trois approches propres, toutes compatibles avec cette architecture :

1. **Dépôt de données privé** — l'app reste publique, `data/` vit dans un dépôt privé
   (il suffit de changer `RACINE_DATA` dans l'app).
2. **Se limiter à son périmètre** — n'héberger que ce que l'on collectionne réellement.
3. **API officielle Numista** — la voie prévue par eux pour un usage applicatif.
