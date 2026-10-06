# CoPubli DRI

Dashboard web de visualisation et d'analyse des **copublications scientifiques**.

Cette version correspond à l'instance **DRI (Direction de la Recherche et de l'Innovation)** de CoPubli.

> **Créé par Andréa NEBOT**  
> Data Analyst / Scientist  
> Membre de l'équipe **DATALAKE**

CoPubli DRI permet d'explorer et de visualiser des indicateurs liés aux copublications et aux collaborations scientifiques.

---

## Sommaire

- [1. Architecture](#1-architecture)
- [2. Prérequis](#2-prérequis)
- [3. Installation locale](#3-installation-locale)
- [4. Gestion des données](#4-gestion-des-données)
- [5. Lancer CoPubli DRI](#5-lancer-copubli-dri)
- [6. Déploiement sur une VM](#6-déploiement-sur-une-vm)
- [7. Configuration SSH](#7-configuration-ssh)
- [8. GitHub et mise à jour du projet](#8-github-et-mise-à-jour-du-projet)
- [9. Déploiement avec Nginx](#9-déploiement-avec-nginx)
- [10. Exécution avec systemd](#10-exécution-avec-systemd)
- [11. Mise à jour de l'application](#11-mise-à-jour-de-lapplication)
- [12. Sécurité](#12-sécurité)
- [13. Dépannage](#13-dépannage)
- [14. Organisation du projet](#14-organisation-du-projet)
- [15. Développement](#15-développement)
- [16. Auteur et équipe](#16-auteur-et-équipe)

---

# 1. Architecture

CoPubli DRI est une application web basée sur **Python / Dash**.

L'architecture de déploiement recommandée est :

```text
                         ┌─────────────────────┐
                         │      Utilisateur    │
                         │      Navigateur     │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / HTTPS
                                    ▼
                         ┌─────────────────────┐
                         │       Nginx         │
                         │   Reverse Proxy     │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP local
                                    ▼
                         ┌─────────────────────┐
                         │     CoPubli DRI     │
                         │     Dash / Flask    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Données locales  │
                         │     DRI / Parquet   │
                         └─────────────────────┘
```

Le dépôt Git contient principalement **le code source**.

Les données de production et les secrets doivent rester en dehors du dépôt.

---

# 2. Prérequis

## Développement local

Prévoir :

- Python 3.9 ou version compatible avec `requirements.txt`
- Git
- pip
- un navigateur web

Vérifier l'installation :

```bash
python3 --version
git --version
python3 -m pip --version
```

## Déploiement sur une VM

Prévoir :

- Linux, typiquement Ubuntu/Debian
- Python 3
- Git
- Nginx
- accès SSH à la VM
- un compte de déploiement
- accès aux données nécessaires à l'application

---

# 3. Installation locale

## 3.1 Cloner le dépôt

Avec SSH :

```bash
git clone git@github.com:Inria-Datalake/copublication-dashboard-dri.git
cd copublication-dashboard-dri
```

Ou avec HTTPS :

```bash
git clone https://github.com/Inria-Datalake/copublication-dashboard-dri.git
cd copublication-dashboard-dri
```

---

## 3.2 Créer un environnement virtuel

```bash
python3 -m venv .venv
```

Activer l'environnement.

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

# 4. Gestion des données

## ⚠️ Important

Les données utilisées par CoPubli DRI peuvent contenir des informations qui ne doivent pas être publiées.

Les fichiers de données ne doivent donc **pas être versionnés dans Git**.

Ne jamais ajouter au dépôt :

```text
*.csv
*.xlsx
*.parquet
```

De même, ne jamais versionner :

```text
.env
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
```

Le fichier `.gitignore` du projet est prévu pour empêcher l'ajout accidentel de ces fichiers.

---

## Exemple d'organisation des données

Sur une machine de déploiement, les données peuvent être stockées dans un répertoire séparé du code :

```text
<DATA_DIR>/
└── dashboard_dri_v3.parquet
```

Par exemple :

```text
<DATA_DIR> = /var/lib/<APPLICATION_NAME>/data
```

Le chemin réel dépend de l'environnement de déploiement et ne doit pas être inscrit dans le dépôt public.

---

## Vérifier avant un commit

Avant de publier une modification :

```bash
git status
```

Puis, si nécessaire :

```bash
git ls-files | grep -E '(\.csv$|\.xlsx$|\.parquet$|\.pem$|\.key$|id_rsa|id_ed25519)'
```

Cette commande ne doit pas retourner de données ou de clés sensibles.

> Ne jamais utiliser `git add -f` pour forcer l'ajout d'un fichier ignoré contenant des données ou des secrets.

---

# 5. Lancer CoPubli DRI

Depuis la racine du projet :

```bash
source .venv/bin/activate
python app.py
```

L'application écoute alors sur le port configuré dans l'application.

En développement, elle peut généralement être consultée depuis :

```text
http://127.0.0.1:<COPUBLI_PORT>
```

où :

```text
<COPUBLI_PORT>
```

désigne le port choisi pour l'instance.

Le port réel doit être configuré selon l'environnement et ne doit pas être supposé à partir de cette documentation.

---

# 6. Déploiement sur une VM

## 6.1 Connexion

Depuis le poste d'administration :

```bash
ssh <DEPLOY_USER>@<VM_HOST>
```

ou avec un alias défini dans la configuration SSH :

```bash
ssh <VM_ALIAS>
```

Les valeurs :

```text
<DEPLOY_USER>
<VM_HOST>
<VM_ALIAS>
```

sont propres à l'infrastructure et ne doivent pas être publiées dans le README.

---

## 6.2 Organisation recommandée

Une organisation possible est :

```text
<APP_ROOT>/
├── copublication-dashboard-dri/
│   ├── app.py
│   ├── callbacks.py
│   ├── data.py
│   ├── layouts/
│   └── assets/
│
└── ...
```

Les données peuvent être séparées :

```text
<DATA_ROOT>/
└── dashboard_dri_v3.parquet
```

L'idée importante est :

```text
Code Git
    ≠
Données de production
```

---

## 6.3 Cloner le projet

```bash
cd <APPS_ROOT>

git clone git@github.com:Inria-Datalake/copublication-dashboard-dri.git

cd copublication-dashboard-dri
```

Créer ensuite l'environnement Python :

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

Il est recommandé d'utiliser **des clés distinctes** pour ces usages.

---

## 7.1 Connexion vers la VM

Depuis le poste d'administration :

```bash
ssh-keygen -t ed25519
```

La clé privée reste sur le poste d'administration.

La clé publique peut être installée sur la VM dans :

```text
~/.ssh/authorized_keys
```

**Ne jamais copier la clé privée sur la VM simplement pour permettre la connexion.**

---

## 7.2 Accès de la VM à GitHub

Si la VM doit effectuer :

```bash
git clone
git pull
git fetch
```

via SSH, créer une clé dédiée.

Exemple :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/<GITHUB_SSH_KEY>
```

Cela crée :

```text
~/.ssh/<GITHUB_SSH_KEY>
~/.ssh/<GITHUB_SSH_KEY>.pub
```

La clé privée reste exclusivement sur la VM.

La clé publique peut être enregistrée auprès de GitHub selon la politique de l'organisation.

---

## 7.3 Configuration SSH

Modifier :

```bash
nano ~/.ssh/config
```

Exemple générique :

```sshconfig
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/<GITHUB_SSH_KEY>
    IdentitiesOnly yes
```

Protéger les permissions :

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/<GITHUB_SSH_KEY>
chmod 644 ~/.ssh/<GITHUB_SSH_KEY>.pub
```

---

## 7.4 Tester l'accès GitHub

```bash
ssh -T git@github.com
```

Un résultat similaire à :

```text
Hi <GITHUB_USER>! You've successfully authenticated, but GitHub does not provide shell access.
```

indique que l'authentification fonctionne.

---

## 7.5 Vérifier quelle clé est utilisée

```bash
ssh -G github.com | grep -i identityfile
```

Puis :

```bash
ssh-keygen -lf ~/.ssh/<GITHUB_SSH_KEY>
```

Ne jamais afficher le contenu d'une clé privée avec :

```bash
cat ~/.ssh/<GITHUB_SSH_KEY>
```

---

# 8. GitHub et mise à jour du projet

## Premier déploiement

```bash
cd <APPS_ROOT>

git clone git@github.com:Inria-Datalake/copublication-dashboard-dri.git

cd copublication-dashboard-dri
```

Vérifier :

```bash
git remote -v
git branch -vv
```

---

## Mise à jour

Avant toute mise à jour :

```bash
git status
```

Si le dépôt est propre :

```bash
git pull --ff-only origin main
```

Puis mettre à jour les dépendances :

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Redémarrer ensuite le service applicatif si nécessaire.

---

# 9. Déploiement avec Nginx

Nginx peut servir de **reverse proxy** devant CoPubli.

Architecture :

```text
Internet
   │
   │ HTTPS
   ▼
┌───────────────┐
│     Nginx     │
└───────┬───────┘
        │
        │ HTTP local
        ▼
┌───────────────┐
│  CoPubli DRI  │
│ 127.0.0.1:<P> │
└───────────────┘
```

---

## 9.1 Installer Nginx

Sur Ubuntu/Debian :

```bash
sudo apt update
sudo apt install nginx
```

Vérifier :

```bash
sudo systemctl status nginx
```

---

## 9.2 Créer la configuration

Créer un fichier Nginx :

```bash
sudo nano /etc/nginx/sites-available/<NGINX_SITE_NAME>
```

Exemple générique :

```nginx
server {
    listen 80;
    server_name <COPUBLI_DOMAIN>;

    location / {
        proxy_pass http://127.0.0.1:<COPUBLI_PORT>;

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

Les valeurs suivantes doivent rester propres à l'environnement :

```text
<COPUBLI_DOMAIN>
<COPUBLI_PORT>
<NGINX_SITE_NAME>
```

---

## 9.3 Activer le site

```bash
sudo ln -s \
    /etc/nginx/sites-available/<NGINX_SITE_NAME> \
    /etc/nginx/sites-enabled/<NGINX_SITE_NAME>
```

Tester la configuration :

```bash
sudo nginx -t
```

Puis recharger :

```bash
sudo systemctl reload nginx
```

---

## 9.4 HTTPS

Pour une application accessible depuis Internet, utiliser HTTPS.

Le certificat TLS doit être géré **au niveau de l'infrastructure** et ne doit jamais être commité dans Git.

Ne jamais placer dans le dépôt :

```text
*.pem
*.key
*.p12
*.pfx
```

---

# 10. Exécution avec systemd

Pour une VM de production, il est recommandé d'exécuter CoPubli avec **systemd** plutôt que dans une session SSH interactive.

Créer un service :

```bash
sudo nano /etc/systemd/system/<COPUBLI_SERVICE>.service
```

Exemple :

```ini
[Unit]
Description=CoPubli DRI Dashboard
After=network.target

[Service]
Type=simple

User=<DEPLOY_USER>
Group=<DEPLOY_USER>

WorkingDirectory=<APP_DIR>

Environment="PATH=<APP_DIR>/.venv/bin"

ExecStart=<APP_DIR>/.venv/bin/python app.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Les valeurs :

```text
<DEPLOY_USER>
<APP_DIR>
<COPUBLI_SERVICE>
```

doivent être adaptées à l'environnement de déploiement.

---

## Activer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable <COPUBLI_SERVICE>
sudo systemctl start <COPUBLI_SERVICE>
```

Vérifier :

```bash
sudo systemctl status <COPUBLI_SERVICE>
```

Consulter les logs :

```bash
sudo journalctl -u <COPUBLI_SERVICE> -f
```

---

# 11. Mise à jour de l'application

Procédure recommandée :

```bash
cd <APP_DIR>
```

Vérifier :

```bash
git status
```

Récupérer les modifications :

```bash
git pull --ff-only origin main
```

Mettre à jour les dépendances :

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Redémarrer :

```bash
sudo systemctl restart <COPUBLI_SERVICE>
```

Vérifier :

```bash
sudo systemctl status <COPUBLI_SERVICE>
```

Consulter les derniers logs :

```bash
sudo journalctl -u <COPUBLI_SERVICE> -n 100 --no-pager
```

---

# 12. Sécurité

## 12.1 Ne jamais versionner de secrets

Ne jamais ajouter au dépôt :

```text
.env
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
```

Ni les données :

```text
*.csv
*.xlsx
*.parquet
```

---

## 12.2 Vérification avant publication

Avant un commit :

```bash
git status
```

Puis :

```bash
git diff --cached --stat
```

et, si nécessaire :

```bash
git diff --cached
```

Vérifier les fichiers suivis :

```bash
git ls-files
```

---

## 12.3 Clés SSH

Une clé privée SSH doit rester privée.

Elle ne doit jamais :

- être ajoutée au dépôt ;
- être publiée sur GitHub ;
- être ajoutée dans un ticket ;
- être envoyée par mail ;
- être copiée dans le répertoire du projet ;
- être incluse directement dans un fichier de configuration versionné.

---

## 12.4 En cas de fuite d'une clé

Si une clé privée est accidentellement publiée :

1. considérer immédiatement la clé comme compromise ;
2. créer une nouvelle clé ;
3. retirer l'ancienne clé des services concernés ;
4. mettre à jour les systèmes qui l'utilisent ;
5. nettoyer l'historique Git si nécessaire ;
6. vérifier que la clé n'est plus présente dans le dépôt.

Supprimer simplement le fichier avec :

```bash
git rm <fichier>
```

ne suffit pas si la clé a déjà été commitée.

---

## 12.5 Données de production

Le dépôt Git doit contenir le code, pas les données de production.

Architecture recommandée :

```text
GitHub
  │
  └── Code source

VM
  ├── Application
  ├── Environnement Python
  └── Données locales
```

---

# 13. Dépannage

## L'application ne répond pas

Vérifier le service :

```bash
sudo systemctl status <COPUBLI_SERVICE>
```

Consulter les logs :

```bash
sudo journalctl -u <COPUBLI_SERVICE> -n 100 --no-pager
```

Tester directement l'application :

```bash
curl http://127.0.0.1:<COPUBLI_PORT>
```

Si l'application répond localement mais pas depuis le navigateur, vérifier Nginx.

---

## Nginx ne fonctionne pas

Tester :

```bash
sudo nginx -t
```

Puis :

```bash
sudo systemctl status nginx
```

Logs :

```bash
sudo journalctl -u nginx -n 100 --no-pager
```

---

## GitHub refuse l'accès SSH

Tester :

```bash
ssh -T git@github.com
```

Vérifier la configuration :

```bash
ssh -G github.com | grep -i identityfile
```

Vérifier l'empreinte :

```bash
ssh-keygen -lf ~/.ssh/<GITHUB_SSH_KEY>
```

Pour un diagnostic détaillé :

```bash
ssh -vT git@github.com
```

Éviter de publier les sorties contenant des informations sensibles.

---

# 14. Organisation du projet

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
│   ├── custom.css
│   ├── dark-mode.css
│   ├── dependencies.html
│   └── ...
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

Les fichiers de données de production ne doivent pas apparaître dans cette structure Git publique.

---

# 15. Développement

Créer une branche :

```bash
git checkout -b feature/<FEATURE_NAME>
```

Développer et tester localement.

Vérifier :

```bash
git status
git diff
```

Ajouter uniquement les fichiers nécessaires :

```bash
git add <FILE_1> <FILE_2>
```

Créer le commit :

```bash
git commit -m "Description de la modification"
```

Publier la branche :

```bash
git push -u origin feature/<FEATURE_NAME>
```

Les modifications peuvent ensuite être intégrées dans `main` selon le processus de revue utilisé par l'équipe.

---

# 16. Auteur et équipe

## Andréa NEBOT

**Data Analyst / Scientist**  
**Membre de l'équipe DATALAKE**

CoPubli DRI a été créé dans le cadre des activités de l'équipe DATALAKE afin de faciliter l'exploration, l'analyse et la visualisation des copublications et collaborations scientifiques.

---

# Principes à retenir

> **GitHub = code source.**

> **VM = application + données locales.**

> **SSH = clés privées uniquement sur les machines qui en ont besoin.**

> **Nginx = reverse proxy et point d'entrée HTTP/HTTPS.**

> **Les données de production ne doivent jamais être versionnées.**

> **Les secrets et clés privées ne doivent jamais être publiés.**
