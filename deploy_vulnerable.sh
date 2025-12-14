#!/bin/bash

# Couleurs
RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m'

echo -e "${RED}=== 💀 DÉPLOIEMENT VULNÉRABLE SHAREPY (LAB RED TEAM) ===${NC}"
echo -e "${ORANGE}[!] ATTENTION : Cette configuration contient 15 failles critiques.${NC}"
echo -e "${ORANGE}[!] NE PAS UTILISER EN PRODUCTION.${NC}"

# 1. Nettoyage
echo -e "${RED}[+] Reset de l'environnement...${NC}"
sudo docker-compose down -v 2>/dev/null

# 2. Création du .env "Passoire" (M1: Secrets en clair)
echo -e "${RED}[+] Injection des secrets faibles (secret123, admin)...${NC}"
cat <<EOF > .env
# CONFIGURATION VULNERABLE
DEBUG=True
ENVIRONMENT=development
DOMAIN=localhost

# Credentials par défaut (M1 / M6)
POSTGRES_USER=admin
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sharepy

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_ENDPOINT=minio:9000

# Weak JWT (M15)
JWT_SECRET=secret123
SECRET_KEY=secret123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# 3. Création des fichiers pièges (M4 / M11)
echo -e "${RED}[+] Création des artefacts vulnérables (Honeypots)...${NC}"

# Création dossier app s'il n'existe pas (pour y mettre les pièges)
mkdir -p app/uploads

# M4: Fichier .env accessible publiquement
cp .env app/.env

# M4: Fichier backup.db
echo "INSERT INTO users (username, password) VALUES ('admin', 'postgres');" > app/backup.db

# M11: Faux dossier .git pour simuler une fuite de repo
mkdir -p app/.git
echo "[core] repositoryformatversion = 0" > app/.git/config

# 4. Lancement
echo -e "${RED}[+] Lancement des services...${NC}"
# On suppose que l'utilisateur est sur la branche 'vulnerable' ou 'main' qui contient le docker-compose avec Adminer
sudo docker-compose up --build -d

echo -e "${RED}=== 💀 ENVIRONNEMENT VULNÉRABLE PRÊT ===${NC}"
echo -e "Application Web : http://localhost"
echo -e "Adminer (DB)    : http://localhost:8080 (Login: admin/postgres)"
echo -e "MinIO Console   : http://localhost:9001 (Login: minioadmin/minioadmin)"
echo -e "API Docs (Debug): http://localhost:8000/docs"
