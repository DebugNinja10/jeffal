# Sécurité

## Modifications réalisées

- **Authentification et autorisations** : protection JWT des routes sensibles et contrôle de propriété par utilisateur et entreprise pour éviter les IDOR.
- **Mots de passe** : hash adaptatif non réversible avec `pwdlib`.
- **Numéros de téléphone** : chiffrement Fernet réversible pour permettre leur affichage et leur réutilisation. Une migration Alembic convertit les données existantes.
- **JWT** : algorithme `HS256` imposé, expiration, `iat`, `iss`, `aud`, `jti` et distinction access/refresh token.
- **Web** : access et refresh tokens dans des cookies `HttpOnly`, `Secure`, `SameSite=Strict`, avec rotation et révocation serveur.
- **CSRF** : cookie dédié et en-tête `X-CSRF-Token` obligatoires pour les requêtes d’écriture utilisant les cookies.
- **Mobile** : avec `X-Client-Type: mobile`, les tokens sont renvoyés en JSON pour un stockage dans Android Keystore ou iOS Keychain.
- **Limitation de connexion** : maximum de 5 échecs par adresse IP et numéro sur 15 minutes.
- **Entrées et fichiers** : limites sur les messages, textes TTS, fichiers audio, montants, identifiants et opérations financières ; types audio contrôlés et lecture par blocs.
- **Agents métier** : contrôle du `business_id`, validation des périodes de rapports et conservation du contexte utilisateur dans les actions.
- **PDF** : échappement des contenus dynamiques avant génération pour empêcher l’interprétation de balises ReportLab.
- **Logs et réponses** : logs SQL détaillés désactivés et réduction des données techniques exposées.
- **En-têtes HTTP** : ajout de protections contre le MIME sniffing, le framing, la fuite de référent et les permissions navigateur ; HSTS en production.
- **Production** : Swagger/ReDoc/OpenAPI désactivés en production et CORS limité aux origines configurées.
- **Secrets et dépendances** : secrets chargés depuis l’environnement, fichiers `.env` exclus de Git, dépendances nécessaires au chiffrement et à l’authentification déclarées.

## Actions manuelles

- Définir `DATABASE_URL`, `SECRET_KEY` (minimum 32 caractères), `ENCRYPTION_KEY` et `GEMINI_API_KEY` si nécessaire.
- Sauvegarder la base puis exécuter `alembic upgrade head` pour chiffrer les téléphones et créer la table des refresh tokens.
- Conserver `ENCRYPTION_KEY` dans un gestionnaire de secrets ; sa perte rend les numéros irrécupérables.
- En production, définir `ENVIRONMENT=production`, `COOKIE_SECURE=true`, HTTPS et `CORS_ORIGINS` avec uniquement les origines autorisées.
- En développement HTTP uniquement, utiliser `COOKIE_SECURE=false`.
- Le frontend web doit envoyer `X-CSRF-Token` pour les requêtes `POST`, `PUT`, `PATCH` et `DELETE` utilisant les cookies.
- Le frontend mobile doit envoyer `X-Client-Type: mobile`, stocker les tokens dans Keystore/Keychain et utiliser `Authorization: Bearer`.
- Le rate limiter actuel est local au processus ; avec plusieurs workers ou instances, le remplacer par un stockage partagé Redis.
