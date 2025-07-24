# Bot de Trading IA Solana

## Aperçu du Projet

Ce projet vise à développer un bot de trading avancé basé sur l'intelligence artificielle pour la blockchain Solana. Le bot exploitera l'analyse de données en temps réel, l'intelligence artificielle (spécifiquement Google Gemini 2.5 Flash) et un module de décision sophistiqué pour identifier et exécuter des opportunités de trading rentables, en se concentrant principalement sur les nouveaux tokens SPL lancés. Une caractéristique clé est l'intégration d'une base de données de réputation locale pour évaluer la fiabilité des tokens et des portefeuilles.

## Exigences Techniques

### Fonctionnalités Principales
- **Surveillance de la Blockchain en Temps Réel**: Écoute les événements de la blockchain Solana (par exemple, nouvelles créations de tokens, changements de pools de liquidité, activités significatives de portefeuilles) via WebSockets.
- **Module de Décision Ultra-Rapide**: Implémente un module hautement optimisé pour des décisions d'achat/vente rapides basées sur des stratégies prédéfinies et l'analyse IA.
- **Analyse IA Passive**: Utilise Google Gemini 2.5 Flash pour l'analyse passive des métadonnées de tokens, du sentiment social (si intégré) et du comportement on-chain afin de générer des scores de risque et des informations.
- **Base de Données de Réputation Locale**: Une base de données SQLite pour stocker et gérer les scores de réputation des portefeuilles et des tokens, influençant les décisions de trading.
- **Exécution des Ordres**: Intégration avec les DEX Solana (par exemple, Raydium, Orca) pour des échanges de tokens efficaces et sécurisés.

### Interface Web (React + Tailwind CSS)
- **Tableau de Bord**: Affichage en temps réel des performances du bot, des avoirs actuels, des transactions récentes et des métriques clés.
- **Gestion des Paramètres**: Interface pour configurer les paramètres du bot, les clés API (par exemple, API Gemini), les stratégies de trading et la tolérance au risque.
- **Visualiseur/Éditeur de Base de Données de Réputation**: Permet l'inspection et la modification manuelles des entrées de réputation.
- **Authentification**: Connexion sécurisée pour accéder à l'interface web.

### Sécurité et Performance
- **Gestion Sécurisée des Clés**: Bonnes pratiques pour la gestion des clés privées Solana et des clés API.
- **Opérations à Faible Latence**: Optimisation de tous les composants pour la vitesse, cruciale pour le trading à haute fréquence.
- **Gestion des Erreurs et Journalisation**: Journalisation robuste et rapports d'erreurs pour la surveillance et le débogage.

### Déploiement
- **Dockerisation**: Conteneurisation de l'application pour un déploiement et une évolutivité faciles.
- **Compatibilité Oracle Free Tier**: Conception du bot pour fonctionner efficacement dans les contraintes de ressources des instances ARM Always Free d'Oracle Cloud.

## Structure du Projet

```
solana-ai-trading-bot/
├── .env.example             # Exemple de variables d'environnement
├── .gitignore               # Fichier .gitignore
├── Dockerfile               # Dockerfile pour la construction de l'application
├── Procfile                 # Pour les déploiements de type Heroku
├── README.md                # README du projet
├── install.sh               # Script pour construire l'image Docker
├── run.sh                   # Script pour exécuter le conteneur Docker
├── backend/                 # Backend FastAPI
│   ├── main.py              # Application FastAPI principale
│   ├── requirements.txt     # Dépendances Python
│   ├── auth/                # Module d'authentification
│   │   └── auth.py
│   ├── blockchain/          # Interaction avec la blockchain Solana
│   │   ├── rpc_client.py
│   │   ├── websocket_listener.py
│   │   └── token_scanner.py
│   ├── config/              # Configuration de l'application
│   │   └── settings.py
│   ├── database/            # Modèles et gestion de la base de données
│   │   └── db.py
│   ├── trading/             # Logique et exécution du trading
│   │   ├── decision_module.py
│   │   ├── order_executor.py
│   │   └── trading_strategies.py
│   ├── ai_analysis/         # Analyse IA et gestion de la réputation
│   │   ├── gemini_analyzer.py
│   │   └── reputation_db_manager.py
│   └── utils/               # Fonctions utilitaires
│       ├── logger.py
│       └── solana_utils.py
├── frontend/                # Frontend React.js
│   ├── public/              # Actifs publics (index.html, favicons, etc.)
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   └── manifest.json
│   ├── src/                 # Code source React
│   │   ├── components/      # Composants réutilisables
│   │   │   ├── Dashboard.js
│   │   │   ├── Login.js
│   │   │   └── PrivateRoute.js
│   │   ├── App.css
│   │   ├── App.js
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── reportWebVitals.js
│   │   └── setupTests.js
│   ├── package.json         # Dépendances du frontend
│   ├── yarn.lock            # Fichier yarn.lock
│   ├── tailwind.config.js   # Configuration Tailwind CSS
│   └── postcss.config.js    # Configuration PostCSS
└──
```

## Installation & Utilisation

### Installation automatisée (Linux/Windows VPS ou local)

1. **Clonez le dépôt ou transférez les fichiers sur votre VPS/local :**
   ```bash
   git clone https://github.com/votre-utilisateur/solana-ai-trading-bot.git
   cd solana-ai-trading-bot
   ```
2. **Lancez le script d’installation automatique :**
   ```bash
   ./install.sh
   ```
   (ou sous Windows : `install_bot.sh`)
   - Le script installe toutes les dépendances, configure le firewall, crée le fichier `.env` et lance le backend + frontend.
3. **Configurez vos clés et paramètres dans l’interface web :**
   - Accédez à l’interface : `http://<IP_DE_TON_VPS>:3000`
   - Connectez-vous avec le login indiqué dans `.env` (par défaut : admin)
   - Renseignez votre clé Gemini, adresse TrustWallet, capital initial, etc. dans l’onglet "Paramètres du Bot".
   - Tous les réglages sont modifiables en temps réel, aucune modification de fichier nécessaire.
4. **Démarrez le bot :**
   ```bash
   ./run.sh
   ```
   (ou relancez `install_bot.sh` après un reboot ou une mise à jour)

### Fonctionnalités principales

- **Dashboard web** : Contrôle total du bot, configuration en temps réel, suivi des performances, logs, IA, sécurité.
- **Automatisation IA** : L’IA analyse et optimise en continu les paramètres du bot grâce aux fichiers logs (`simulation_trades.log`, `real_trades.log`). À chaque trade, l’optimisation est déclenchée automatiquement.
- **Gestion du capital** : Choix du montant de SOL à investir depuis l’interface. Le bot vérifie que ce montant ne dépasse jamais le solde TrustWallet. Tous les gains sont automatiquement réinvestis.
- **Sécurité** : Clés et infos sensibles stockées dans `.env` et modifiables uniquement via l’interface sécurisée. Firewall configuré automatiquement.
- **Logs** : Deux fichiers logs (`simulation_trades.log`, `real_trades.log`) sont générés automatiquement pour l’analyse IA et le suivi des performances.
- **Maintenance** : Pour mettre à jour le bot, remplacez les fichiers et relancez le script d’installation.

### Développement

#### Backend (FastAPI)
1.  **Installer les dépendances Python :**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
2.  **Exécuter l'application FastAPI :**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    La documentation de l'API sera disponible à l'adresse `http://localhost:8000/docs`.

#### Frontend (React)
1.  **Installer les dépendances Node.js :**
    ```bash
    cd frontend
    yarn install
    ```
2.  **Démarrer le serveur de développement React :**
    ```bash
    yarn start
    ```
    Le frontend s'exécutera généralement sur `http://localhost:3000` (ou un autre port disponible).

## FAQ rapide

- **Comment accéder à l’interface ?**
  → http://<IP_DE_TON_VPS>:3000
- **Comment changer la clé Gemini, TrustWallet ou le capital ?**
  → Onglet "Paramètres du Bot" dans le dashboard web
- **Comment voir les logs ?**
  → Onglet "Aperçu" ou fichiers de log sur le VPS
- **Comment ajouter une réputation manuelle ?**
  → Onglet "Base de Données de Réputation" dans le dashboard
- **Comment sécuriser l’accès ?**
  → Changez le mot de passe dans `.env` ou via l’interface

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour les bugs et les demandes de fonctionnalités.

## Licence

Ce projet est sous licence MIT.