#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction du catalogue du Médaillier.
© 2026 Kévin François Cagnat

Prend des fichiers de pièces bruts (compléments JSON extraits de Numista)
et produit l'arborescence `data/` du dépôt, prête à publier sur GitHub.

Principe :
  - chaque MODULE est un périmètre de collection (zone euro, France ancienne, antiques…)
  - chaque module produit :
      index.json    → fiches ALLÉGÉES (118 o/pièce) : tout ce qu'il faut pour
                      chercher, lister, filtrer, détecter les séries
      f/NNN.json    → fiches COMPLÈTES par paquets (chargées à la demande)
  - data/manifest.json recense les modules (version, taille, nb de pièces)

Usage :
    python3 outils/construire-catalogue.py

Ajouter un module : compléter la liste MODULES ci-dessous.
"""
import json, os, re, shutil, hashlib

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(RACINE, "pwa", "data")   # racine du site publie
SOURCES = os.path.join(RACINE, "sources")     # compléments JSON bruts
PAR_PAQUET = 400                              # fiches complètes par fichier

# --------------------------------------------------------------------------
# Déclaration des modules. `filtre` reçoit une pièce, renvoie True/False.
# --------------------------------------------------------------------------
def est_circulante(p):
    v = p.get("valeurFaciale") or ""
    m = re.match(r"^(\d+(?:[.,]\d+)?)\s*(euro|cent)s?$", v.strip(), re.I)
    if not m:
        return False
    val = float(m.group(1).replace(",", "."))
    return m.group(2).lower().startswith("cent") or val in (1.0, 2.0)

MODULES = [
    {
        "id": "euro-circulantes",
        "libelle": "Zone euro — pièces circulantes",
        "description": "Cents, 1 € et 2 € des 27 émetteurs (courantes et commémoratives).",
        "source": "catalogue-zone-euro-COMPLET.json",
        "filtre": est_circulante,
        "defaut": True,
    },
    {
        "id": "euro-collection",
        "libelle": "Zone euro — pièces de collection",
        "description": "Or, argent, BE/BU : 5 €, 10 €, 50 €, 100 €… Non circulantes.",
        "source": "catalogue-zone-euro-COMPLET.json",
        "filtre": lambda p: not est_circulante(p),
        "defaut": False,
    },
]

# --------------------------------------------------------------------------
CATEGORIES = [
    "Pièce courante", "Pièce circulante commémorative", "Pièce non circulante",
    "Pièce pour collectionneurs", "Monnaie de siège", "Monnaie de nécessité officielle",
    "Jeton de marchand", "Pièce locale", "Essai", "Fausse monnaie d'époque", "Proto-monnaie",
]

def id_numista(p):
    m = re.search(r"pieces(\d+)", p.get("lienNumista") or "")
    return m.group(1) if m else None

def categoriser(p):
    if p.get("categorie") in CATEGORIES:
        return p["categorie"]
    t = ((p.get("nom") or "") + " " + (p.get("notes") or "")).lower()
    if re.search(r"proto-?monnaie", t):        return "Proto-monnaie"
    if re.search(r"fausse monnaie|contrefa", t): return "Fausse monnaie d'époque"
    if re.search(r"\bessai\b|pi[eé]fort", t):  return "Essai"
    if re.search(r"monnaie de si[eè]ge", t):   return "Monnaie de siège"
    if re.search(r"jeton", t):                 return "Jeton de marchand"
    if re.search(r"n[eé]cessit[eé]", t):       return "Monnaie de nécessité officielle"
    if re.search(r"(pi[eè]ce|monnaie) locale", t): return "Pièce locale"
    if re.search(r"comm[eé]morat", t):
        return "Pièce circulante commémorative" if est_circulante(p) else "Pièce pour collectionneurs"
    return "Pièce courante" if est_circulante(p) else "Pièce pour collectionneurs"

def allege(p):
    """Fiche allégée : uniquement les champs utiles à la recherche/liste/détection.
    Clés courtes pour diviser le poids par 5."""
    i = id_numista(p)
    o = {"i": i, "n": p.get("nom"), "p": (p.get("match") or {}).get("pays")}
    an = (p.get("match") or {}).get("annee")
    if an: o["a"] = an
    if p.get("valeurFaciale"): o["f"] = p["valeurFaciale"]
    o["c"] = categoriser(p)
    if p.get("numeroKM"): o["k"] = p["numeroKM"]
    # vignette : on ne stocke que le chemin relatif, l'app reconstruit l'URL
    av = p.get("imageAvers")
    if av and "/photos/" in av:
        o["v"] = av.split("/photos/", 1)[1]
    return o

BASE_IMG = "https://en.numista.com/catalogue/photos/"

def construire():
    if os.path.isdir(DATA):
        shutil.rmtree(DATA)
    os.makedirs(DATA)

    cache_sources = {}
    manifeste = {
        "description": "Manifeste des catalogues du Médaillier. L'app lit ce fichier, "
                       "puis ne télécharge que les modules activés par l'utilisateur.",
        "version": 2,
        "baseImages": BASE_IMG,
        "categories": CATEGORIES,
        "modules": [],
    }

    for mod in MODULES:
        src = mod["source"]
        if src not in cache_sources:
            chemin = os.path.join(SOURCES, src)
            cache_sources[src] = json.load(open(chemin, encoding="utf-8"))["pieces"]
        pieces = [p for p in cache_sources[src] if mod["filtre"](p)]
        pieces.sort(key=lambda p: ((p.get("match") or {}).get("pays") or "", p.get("nom") or ""))

        dossier = os.path.join(DATA, "modules", mod["id"])
        os.makedirs(os.path.join(dossier, "f"), exist_ok=True)

        # 1) Index allégé + table de correspondance pièce → paquet
        index = []
        for n, p in enumerate(pieces):
            a = allege(p)
            a["b"] = n // PAR_PAQUET          # numéro du paquet contenant la fiche complète
            index.append(a)
        chemin_index = os.path.join(dossier, "index.json")
        json.dump({"id": mod["id"], "n": len(pieces), "parPaquet": PAR_PAQUET, "pieces": index},
                  open(chemin_index, "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))

        # 2) Fiches complètes par paquets
        nb_paquets = 0
        for k in range(0, len(pieces), PAR_PAQUET):
            paquet = pieces[k:k + PAR_PAQUET]
            for p in paquet:
                p["categorie"] = categoriser(p)
            nom = f"{k // PAR_PAQUET:03d}.json"
            json.dump({"pieces": paquet},
                      open(os.path.join(dossier, "f", nom), "w", encoding="utf-8"),
                      ensure_ascii=False, separators=(",", ":"))
            nb_paquets += 1

        taille_index = os.path.getsize(chemin_index)
        taille_totale = sum(
            os.path.getsize(os.path.join(dossier, "f", f))
            for f in os.listdir(os.path.join(dossier, "f"))
        ) + taille_index

        manifeste["modules"].append({
            "id": mod["id"],
            "libelle": mod["libelle"],
            "description": mod["description"],
            "chemin": f"modules/{mod['id']}",
            "nbPieces": len(pieces),
            "nbPaquets": nb_paquets,
            "parPaquet": PAR_PAQUET,
            "tailleIndex": f"{taille_index/1e6:.2f} Mo",
            "tailleTotale": f"{taille_totale/1e6:.2f} Mo",
            "version": 1,
            "defaut": mod["defaut"],
        })
        print(f"  {mod['id']:24} {len(pieces):6} pièces | index {taille_index/1e6:5.2f} Mo "
              f"| {nb_paquets:3} paquets | total {taille_totale/1e6:6.2f} Mo")

    json.dump(manifeste, open(os.path.join(DATA, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\nManifeste : {len(manifeste['modules'])} modules")

if __name__ == "__main__":
    print("Construction du catalogue…")
    construire()
