#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== 🛡️ DÉPLOIEMENT SÉCURISÉ SHAREPY (PROD) ===${NC}"

# 1. Vérification des prérequis
if ! [ -x "$(command -v docker-compose)" ]; then
  echo -e "${RED}[ERREUR] docker-compose n'est pas installé.${NC}"
  exit 1
fi

# 2. Nettoyage de l'existant
echo -e "${BLUE}[+] Nettoyage de l'environnement précédent...${NC}"
sudo docker-compose down -v 2>/dev/null

# 3. Génération des Secrets (Le cœur de la sécurité)
echo -e "${BLUE}[+] Génération des secrets cryptographiques...${NC}"
DB_PASS=$(openssl rand -hex 24)
MINIO_PASS=$(openssl rand -hex 24)
JWT_SECRET=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)

# 4. Création du fichier .env dynamique
echo -e "${BLUE}[+] Création du fichier .env sécurisé...${NC}"
cat <<EOF > .env
# Configuration de Production (Générée automatiquement)
DEBUG=False
ENVIRONMENT=production
DOMAIN=localhost

# Database (Least Privilege)
POSTGRES_USER=sharepy_owner
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_DB=sharepy

# MinIO (Service Account)
MINIO_ROOT_USER=admin_storage
MINIO_ROOT_PASSWORD=$MINIO_PASS
MINIO_ACCESS_KEY=sharepy-backend
MINIO_SECRET_KEY=$MINIO_PASS
MINIO_ENDPOINT=minio:9000

# Security Keys
JWT_SECRET=$JWT_SECRET
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# 5. Sécurisation des permissions
chmod 600 .env
echo -e "${GREEN}[OK] Fichier .env généré et verrouillé (chmod 600).${NC}"

# 6. Lancement de l'infrastructure
echo -e "${BLUE}[+] Lancement des conteneurs (Build & Detach)...${NC}"
sudo docker-compose up --build -d

# 7. Attente de santé (Optionnel)
echo -e "${BLUE}[+] Attente de l'initialisation des services...${NC}"
sleep 10

echo -e "${GREEN}=== ✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS ===${NC}"
echo -e "Application accessible sur : http://localhost"
echo -e "Logs de sécurité : ./logs/security.log"
