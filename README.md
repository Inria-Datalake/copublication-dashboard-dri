# CoPubli DRI

Dashboard web de visualisation et d'analyse des **copublications scientifiques** de l'Inria DataLake.

Cette version correspond à l'instance **DRI (Direction de la Recherche et de l'Innovation)** de CoPubli.

> **Créé par Andréa NEBOT**  
> Data Analyst / Scientist  
> Membre de l'équipe **DATALAKE**

L'application est développée pour faciliter l'exploration, l'analyse et la visualisation des collaborations scientifiques et des copublications.

---

## Sommaire

- [1. Architecture](#1-architecture)
- [2. Prérequis](#2-prérequis)
- [3. Installation locale](#3-installation-locale)
- [4. Données](#4-données)
- [5. Lancer CoPubli DRI](#5-lancer-copubli-dri)
- [6. Déploiement sur une VM](#6-déploiement-sur-une-vm)
- [7. Configuration SSH](#7-configuration-ssh)
- [8. Cloner et mettre à jour le projet depuis GitHub](#8-cloner-et-mettre-à-jour-le-projet-depuis-github)
- [9. Déployer avec Nginx](#9-déployer-avec-nginx)
- [10. Faire tourner CoPubli automatiquement](#10-faire-tourner-copubli-automatiquement)
- [11. Mise à jour de l'application](#11-mise-à-jour-de-lapplication)
- [12. Sécurité](#12-sécurité)
- [13. Dépannage](#13-dépannage)
- [14. Organisation des fichiers](#14-organisation-des-fichiers)
- [15. Développement](#15-développement)

---

# 1. Architecture

CoPubli DRI est composé de plusieurs éléments :

```text
                         ┌─────────────────────┐
                         │      Utilisateur    │
                         │      Navigateur     │
                         └──────────┬──────────┘
                                    │ HTTP/HTTPS
                                    ▼
                         ┌─────────────────────┐
                         │       Nginx         │
                         │   reverse proxy     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Dash / Flask    │
                         │     application     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Données locales DRI │
                         │   CSV / Parquet     │
                         └─────────────────────┘
```

GitHub contient le **code source** de l'application.

Les données volumineuses ou sensibles utilisées par l'instance DRI doivent rester **hors du dépôt Git**.

---

# 2. Prérequis

## Développement local

Prévoir :

- Python 3.9 ou version compatible avec `requirements.txt`
- Git
- pip
- un navigateur web

Vérifier :

```bash
python3 --version
git --version
pip --version
```

## Déploiement VM

Pour une VM Linux :

- Ubuntu/Debian recommandé
- Python 3
- Git
- Nginx
- accès SSH
- utilisateur Linux dédié ou compte de déploiement
- accès aux données DRI

---

# 3. Installation locale

## 3.1 Cloner le dépôt

```bash
git clone git@github.com:Inria-Datalake/copublication-dashboard-dri.git
cd copublication-dashboard-dri
```

Pour utiliser HTTPS :

```bash
git clone https://github.com/Inria-Datalake/copublication-dashboard-dri.git
cd copublication-dashboard-dri
```

---

## 3.2 Créer un environnement virtuel

```bash
python3 -m venv .venv
```

Activer l'environnement :

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3.3 Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 4. Données

## Important

Les données de production **ne doivent pas être ajoutées au dépôt Git**.

En particulier, ne jamais commiter :

```text
*.csv
*.xlsx
*.parquet
.env
*.pem
*.key
id_rsa
id_ed25519
```

Le projet contient un `.gitignore` destiné à empêcher leur publication.

Une donnée DRI peut être stockée localement, par exemple :

```text
/home/<user>/data/copubli/
└── dashboard_dri_v3.parquet
```

Les données de production doivent rester séparées du code source autant que possible.

Avant chaque commit :

```bash
git status
```

Vérifier également :

```bash
git ls-files | grep -E '(\.csv$|\.xlsx$|\.parquet$|\.pem$|\.key$|id_rsa|id_ed25519)'
```

Cette commande ne devrait retourner **aucune donnée ou clé sensible**.

> Ne jamais utiliser `git add -f` pour forcer l'ajout d'un fichier de données ou d'une clé.

---

# 5. Lancer CoPubli DRI

Depuis la racine du projet :

```bash
source .venv/bin/activate
python app.py
```

L'application Dash démarre alors sur l'adresse et le port configurés dans `app.py`.

En développement, accéder à l'application depuis le navigateur via :

```text
http://127.0.0.1:<PORT>
```

Le port exact doit être vérifié dans la configuration de l'application.

---

# 6. Déploiement sur une VM

## 6.1 Connexion à la VM

Depuis le poste local :

```bash
ssh <utilisateur>@<adresse-vm>
```

Si un alias SSH est configuré :

```bash
ssh pocdatalake
```

---

## 6.2 Organisation recommandée

Il est recommandé de séparer le code et les données :

```text
/home/<user>/
├── apps/
│   └── copublication-dashboard-dri/
│
└── data/
    └── copubli/
```

Les données DRI ne doivent pas être mélangées avec les fichiers versionnés par Git lorsque cela peut être évité.

---

## 6.3 Cloner le projet

```bash
cd ~/apps
git clone git@github.com:Inria-Datalake/copublication-dashboard-dri.git
cd copublication-dashboard-dri
```

---

## 6.4 Créer l'environnement Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

# 7. Configuration SSH

SSH peut être utilisé pour deux usages distincts :

1. se connecter à la VM ;
2. permettre à la VM d'accéder à GitHub.

Ces deux usages doivent être séparés autant que possible.

## 7.1 SSH poste local → VM

La clé privée reste uniquement sur le poste local.

La clé publique peut être installée sur la VM dans :

```text
~/.ssh/authorized_keys
```

Ne jamais copier une clé privée sur une VM simplement pour permettre une connexion SSH.

## 7.2 SSH VM → GitHub

Si la VM doit récupérer le code depuis GitHub, créer une clé dédiée :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/github_pocdatalake
```

La clé privée :

```text
~/.ssh/github_pocdatalake
```

reste uniquement sur la VM.

La clé publique :

```text
~/.ssh/github_pocdatalake.pub
```

peut être enregistrée dans GitHub selon la politique de l'organisation.

## 7.3 Configuration SSH

Dans :

```bash
nano ~/.ssh/config
```

Exemple :

```sshconfig
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_pocdatalake
    IdentitiesOnly yes
```

Puis :

```bash
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/github_pocdatalake
chmod 644 ~/.ssh/github_pocdatalake.pub
```

Tester :

```bash
ssh -T git@github.com
```

Un résultat du type :

```text
Hi <github-user>! You've successfully authenticated, but GitHub does not provide shell access.
```

indique que l'authentification fonctionne.

---

# 8. Cloner et mettre à jour le projet depuis GitHub

## Premier déploiement

```bash
cd ~/apps
git clone git@github.com:Inria-Datalake/copublication-dashboard-dri.git
cd copublication-dashboard-dri
```

Vérifier :

```bash
git remote -v
git branch -vv
```

## Mise à jour

```bash
cd ~/apps/copublication-dashboard-dri
git status
git pull --ff-only origin main
```

Puis :

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Redémarrer ensuite l'application si elle tourne comme service.

---

# 9. Déployer avec Nginx

Nginx sert de **reverse proxy** devant l'application Dash.

```text
Navigateur
    │
    │ HTTPS
    ▼
  Nginx
    │
    │ HTTP local
    ▼
Dash / Flask
127.0.0.1:<PORT>
```

## 9.1 Installer Nginx

```bash
sudo apt update
sudo apt install nginx
```

Vérifier :

```bash
sudo systemctl status nginx
```

## 9.2 Configuration

Créer :

```bash
sudo nano /etc/nginx/sites-available/copubli-dri
```

Exemple :

```nginx
server {
    listen 80;
    server_name copubli.example.org;

    location / {
        proxy_pass http://127.0.0.1:8050;

        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
```

Adapter le nom DNS et le port à l'installation réelle.

Activer :

```bash
sudo ln -s \
  /etc/nginx/sites-available/copubli-dri \
  /etc/nginx/sites-enabled/copubli-dri
```

Tester :

```bash
sudo nginx -t
```

Puis :

```bash
sudo systemctl reload nginx
```

Pour une instance exposée sur Internet, configurer également HTTPS/TLS et les règles de sécurité adaptées à l'infrastructure.

---

# 10. Faire tourner CoPubli automatiquement

Pour une VM de production, utiliser **systemd** plutôt qu'un terminal SSH ouvert.

Créer :

```bash
sudo nano /etc/systemd/system/copubli-dri.service
```

Exemple :

```ini
[Unit]
Description=CoPubli DRI Dashboard
After=network.target

[Service]
Type=simple

User=abapst
Group=abapst

WorkingDirectory=/home/abapst/apps/copublication-dashboard-dri

Environment="PATH=/home/abapst/apps/copublication-dashboard-dri/.venv/bin"

ExecStart=/home/abapst/apps/copublication-dashboard-dri/.venv/bin/python app.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Adapter les chemins et l'utilisateur à la VM.

Activer :

```bash
sudo systemctl daemon-reload
sudo systemctl enable copubli-dri
sudo systemctl start copubli-dri
```

Vérifier :

```bash
sudo systemctl status copubli-dri
```

Logs :

```bash
sudo journalctl -u copubli-dri -f
```

---

# 11. Mise à jour de l'application

```bash
cd ~/apps/copublication-dashboard-dri
git status
git pull --ff-only origin main
```

Mettre à jour les dépendances :

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Redémarrer :

```bash
sudo systemctl restart copubli-dri
```

Vérifier :

```bash
sudo systemctl status copubli-dri
```

Puis :

```bash
sudo journalctl -u copubli-dri -n 100 --no-pager
```

---

# 12. Sécurité

## Ne jamais commiter de secrets

Ne jamais ajouter :

```text
.env
*.pem
*.key
id_rsa
id_ed25519
*.p12
*.pfx
*.csv
*.xlsx
*.parquet
```

Avant chaque push :

```bash
git status
git diff --cached --stat
```

Les données de production et les secrets doivent rester hors du dépôt Git.

## Clés privées

Une clé privée SSH ne doit jamais :

- être envoyée dans GitHub ;
- être copiée dans le dossier du projet ;
- être envoyée par mail ;
- être ajoutée à un ticket ;
- être ajoutée à un fichier versionné ;
- être affichée dans un terminal partagé.

## En cas de fuite d'une clé

Une clé privée publiée doit être considérée comme **compromise**.

Il faut :

1. créer une nouvelle clé ;
2. retirer l'ancienne clé des services concernés ;
3. mettre à jour les serveurs ou services qui l'utilisent ;
4. nettoyer l'historique Git si nécessaire ;
5. vérifier que la clé n'est plus présente dans le dépôt.

---

# 13. Dépannage

## L'application ne répond pas

```bash
sudo systemctl status copubli-dri
```

Puis :

```bash
sudo journalctl -u copubli-dri -n 100 --no-pager
```

Tester directement :

```bash
curl http://127.0.0.1:8050
```

Si l'application répond localement mais pas via le navigateur, vérifier Nginx.

## Nginx

```bash
sudo nginx -t
sudo systemctl status nginx
```

Logs :

```bash
sudo journalctl -u nginx -n 100 --no-pager
```

## GitHub / SSH

```bash
ssh -T git@github.com
```

Vérifier la clé utilisée :

```bash
ssh -G github.com | grep -i identityfile
```

Vérifier son empreinte :

```bash
ssh-keygen -lf ~/.ssh/github_pocdatalake
```

---

# 14. Organisation des fichiers

Structure indicative :

```text
copublication-dashboard-dri/
│
├── app.py
├── callbacks.py
├── data.py
├── style.py
├── requirements.txt
├── Dockerfile
├── .gitignore
│
├── assets/
│
├── layouts/
│   ├── __init__.py
│   ├── country_evolution_tab.py
│   ├── filters_kpi.py
│   ├── main_charts.py
│   ├── map_tab.py
│   ├── network_tab.py
│   ├── share_tab.py
│   └── wordcloud_tab.py
│
└── scripts / fichiers auxiliaires
```

Les données locales ne doivent pas être incluses dans cette structure Git publiée.

---

# 15. Développement

Créer une branche :

```bash
git checkout -b feature/ma-fonctionnalite
```

Développer et tester localement.

Vérifier :

```bash
git status
git diff
```

Ajouter uniquement les fichiers nécessaires :

```bash
git add app.py callbacks.py data.py
```

Créer le commit :

```bash
git commit -m "Ajout de ma fonctionnalité"
```

Publier :

```bash
git push -u origin feature/ma-fonctionnalite
```

---

# Auteur et équipe

**Andréa NEBOT**  
*Data Analyst / Scientist*  
*Membre de l'équipe DATALAKE*

CoPubli DRI a été développé pour fournir une interface de visualisation et d'analyse des copublications scientifiques dans le contexte des activités de l'Inria DataLake.

---

# Principes à retenir

> **GitHub = code source.**

> **VM = application + données locales.**

> **SSH = clés privées uniquement sur les machines qui en ont besoin.**

> **Nginx = point d'entrée HTTP/HTTPS et reverse proxy vers Dash.**

> **Ne jamais versionner les données de production ni les secrets.**
