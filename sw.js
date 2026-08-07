/* Service worker — Le Médaillier
   Stratégie "réseau d'abord, cache en secours" pour la coquille de l'app.

   Ce qui est mis en cache : uniquement les fichiers de l'application
   (page, icônes, manifeste). Volontairement PAS :
     - les catalogues data/modules/** → déjà stockés déchiffrés dans IndexedDB
       (les garder aussi ici doublerait l'espace occupé pour rien) ;
     - les images Numista (autre domaine) → des milliers de fichiers qui
       satureraient le quota du navigateur ;
     - les requêtes non-GET.
*/
const CACHE = "medaillier-v22";
const FICHIERS = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png",
  "./series-donnees.json", "./data/manifest.json",
  "./LICENSE", "./README.md"
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      // addAll échoue en bloc si un seul fichier manque : on installe un par un
      .then(c => Promise.all(FICHIERS.map(f => c.add(f).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(cles => Promise.all(cles.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* Faut-il conserver cette réponse en cache ? */
function aMettreEnCache(url) {
  if (url.origin !== self.location.origin) return false;   // images Numista & co.
  if (url.pathname.includes("/data/modules/")) return false; // catalogues → IndexedDB
  return true;
}

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);

  e.respondWith(
    fetch(e.request)
      .then(rep => {
        if (rep && rep.ok && aMettreEnCache(url)) {
          const copie = rep.clone();
          caches.open(CACHE).then(c => c.put(e.request, copie)).catch(() => {});
        }
        return rep;
      })
      .catch(async () => {
        const enCache = await caches.match(e.request);
        if (enCache) return enCache;
        // Hors-ligne : ne renvoyer la page d'accueil que pour une navigation.
        // (La renvoyer pour un .json casserait la lecture des données.)
        if (e.request.mode === "navigate") return caches.match("./index.html");
        return new Response("", { status: 504, statusText: "Hors ligne" });
      })
  );
});
