# 📂 Projet 3 : SharePy - Misconfig Mayhem
### Lab pratique OWASP A02:2025 - Security Misconfiguration

**Auteur :** Abdennour CHAHAT
**Branche :** `vulnerable` (Semaine 1 - Red Team)
**Date :** Décembre 2025

---

## 📝 Description
SharePy est une application de partage de fichiers (type "Mini-Dropbox") construite avec **FastAPI**, **PostgreSQL**, **MinIO** et **Nginx**.

⚠️ **ATTENTION :** Cette version (`vulnerable`) est **intentionnellement non sécurisée**. Elle contient **15 mauvaises configurations critiques** basées sur le Top 10 OWASP A02:2025. Ne pas déployer sur un serveur public !

---

## 🚀 Installation & Démarrage

### Prérequis
* Docker & Docker Compose
* Git

### Lancement
1. Cloner le dépôt et basculer sur la branche vulnérable :
   ```bash
   git clone https://github.com/ch47t/SharePy-Misconfig-Lab.git
   cd sharepy_project
   git checkout vulnerable
   ```

2. Lancer l'infrastructure :
   ```bash
   sudo docker-compose up --build -d
   sudo docker-compose restart backend
   ```

3. L'application est accessible sur : **http://localhost**

---

## 🌍 Accès aux Services

| Service | URL | Identifiants (Si nécessaire) |
|---------|-----|------------------------------|
| **Application Web** | `http://localhost` | Inscription libre |
| **Adminer (DB)** | `http://localhost:8080` | Serveur: `db`, User: `admin`, Pass: `postgres` |
| **Console MinIO** | `http://localhost:9001` | User: `minioadmin`, Pass: `minioadmin` |
| **API Backend** | `http://localhost:8000/docs` | - |

---

## 🚩 Liste des 15 Misconfigurations (Guide de Correction)

Voici comment vérifier/exploiter les 15 failles implémentées dans cette version :

### 1. Infrastructure & Fichiers
* **M1 - Secrets en clair :** Voir le fichier `.env` ou `docker-compose.yml` sur le dépôt Git (contient les mots de passe DB).
* **M3 - Directory Listing :** Aller sur [http://localhost/uploads/](http://localhost/uploads/) pour voir la liste des fichiers bruts.
* **M4 - Fichiers Sensibles :** Exécuter `curl http://localhost/.env` ou `curl http://localhost/backup.db`.
* **M11 - Verbosité Nginx :** Aller sur une page inexistante (ex: `/goprod`). Le header `X-Debug-File-Path` révèle le chemin absolu `/app/...`.
* **M12 - Ports Exposés :** La DB est accessible directement : `psql -h localhost -U admin -d sharepy`.

### 2. Code & Application
* **M2 - Debug Mode & Stack Trace :** Aller sur `/register`. Créer un user, puis **réessayer avec le même pseudo**. Le crash affiche le code source Python (page jaune).
* **M7 - CORS Wildcard :** `curl -I -H "Origin: http://evil.com" http://localhost/api/users/me` montre `Access-Control-Allow-Origin: *`.
* **M10 - Banner Grabbing :** `curl -I http://localhost` révèle `Server: nginx/1.29.4`.
* **M14 - Environment Dump :** Aller sur [http://localhost/debug/info](http://localhost/debug/info) pour voir toutes les variables d'environnement (mots de passe inclus).

### 3. Authentification & Accès
* **M5 - Adminer Public :** Accès libre à [http://localhost:8080](http://localhost:8080) sans VPN ni auth préalable.
* **M6 - MinIO Default Creds :** Accès à [http://localhost:9001](http://localhost:9001) avec `minioadmin` / `minioadmin`.
* **M15 - Weak JWT Secret :** Le secret est `secret123`. Vérifiable sur [jwt.io](https://jwt.io) avec un token récupéré après login.

### 4. Client Side & Uploads
* **M8 - Missing Security Headers :** Aucun header `X-Frame-Options` ou `CSP` présent dans les réponses.
* **M9 - Insecure Cookies :** Après login, inspecter le cookie `session_token`. Les drapeaux `HttpOnly` et `Secure` sont absents (vulnérable au vol par XSS).
* **M13 - Unrestricted Upload (RCE) :** Sur la page `Profile`, uploader un fichier `.html` ou `.php`. Il est accessible et exécutable dans `/uploads/`.

---

## 🛠️ Stack Technique
* **Frontend :** HTML5 / CSS3 (Jinja2 Templates)
* **Backend :** Python FastAPI (Mode Debug)
* **Database :** PostgreSQL 15
* **Storage :** MinIO (S3 Compatible)
* **Server :** Nginx (Reverse Proxy mal configuré)

---
