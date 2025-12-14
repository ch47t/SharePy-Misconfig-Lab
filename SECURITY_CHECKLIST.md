# ✅ SharePy : Checklist "Secure by Default"

Ce document récapitule les standards de sécurité appliqués pour passer de l'état "Vulnérable" à "Durci".

## 🏗️ 1. Infrastructure & Orchestration
- [x] **Secrets :** Aucun mot de passe en clair dans `docker-compose.yml` ou le code. Utilisation exclusive de variables d'environnement (`.env`).
- [x] **Isolation Base de Données :** Port 5432 non exposé sur l'hôte. Accessible uniquement via le réseau interne Docker.
- [x] **Surface d'attaque réduite :** Suppression des services inutiles (ex: Adminer) et des fichiers de débug.
- [x] **Least Privilege :** Le backend n'utilise pas le compte `root` de MinIO ni le superadmin de PostgreSQL.

## 🌐 2. Serveur Web (Nginx)
- [x] **Banner Grabbing :** Version de Nginx masquée (`server_tokens off`).
- [x] **Headers de Sécurité :**
  - `X-Frame-Options: SAMEORIGIN` (Anti-Clickjacking)
  - `X-Content-Type-Options: nosniff` (Anti-MIME Sniffing)
  - `Content-Security-Policy` (CSP) stricte.
- [x] **Contrôle d'accès :**
  - Listing de répertoires désactivé (`autoindex off`).
  - Blocage des fichiers sensibles (`.env`, `.git`, `Dockerfile`, `*.db`).

## 🐍 3. Application Backend (FastAPI)
- [x] **Mode Production :** Debug désactivé (`debug=False`). Pas de Stack Trace en cas d'erreur 500.
- [x] **Authentification :** JWT signé avec une clé forte (générée via OpenSSL).
- [x] **Cookies :** Attributs `HttpOnly` et `SameSite=Strict` activés.
- [x] **Uploads :** Validation stricte des extensions (Whitelist : images/pdf uniquement). Pas d'exécution de scripts (`.php`, `.sh`).
- [x] **CORS :** Liste blanche stricte (pas de `*`).

## 🛡️ 4. Défense Active & Monitoring
- [x] **Logs :** Format structuré JSON centralisé sur l'hôte.
- [x] **IPS (Fail2ban) :** Bannissement automatique des IPs générant des erreurs 401/403 répétées.
