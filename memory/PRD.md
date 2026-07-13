# SportConnect — PRD

## Problème / Vision
"Doctolib du sport" — relier clubs de sport et pratiquants. V1 pilote **Haute-Garonne (31)**.
Web app responsive (React + FastAPI + MongoDB). Extension nationale + mobile natif en phases ultérieures.

## Personas
- **Participant / parent** : cherche, compare, s'inscrit et paie en ligne.
- **Club** : revendique/gère sa page, inscriptions, licenciés, abonnement par paliers.
- **Admin plateforme** : import open data, modération des revendications, suivi.

## Choix utilisateur (V1)
- Auth : **JWT classique** (email + mot de passe, cookie httpOnly).
- Données : **import réel open data Data-ES** (equipements.sports.gouv.fr) filtré dep 31.
- Intégrations : **Stripe + e-mails MOCKÉS** (payment_status="paid" mock_payment=true ; e-mails loggés `[EMAIL MOCK]`).
- Priorité : parcours public + inscription/paiement. Design : agent (identité sport, orange Blaze + obsidian, fonts Cabinet Grotesk/Satoshi).

## Architecture
- Backend `server.py` : auth (/api/auth/*), recherche clubs, fiche, enroll (paiement mock), claim, espace club (mine/PUT/registration/enrollments/subscribe/announce), admin (stats/claims/resolve). RBAC participant/club/admin.
- Import `import_data.py` : regroupe 4000 équipements → 1949 clubs (pages fantômes), 30 clubs actifs (owner club@sportconnect.fr). 28 disciplines.
- Frontend : Home (hero + recherche 3 champs), Results (cartes + carte géo custom du 31), ClubDetail (badge statut + inscription/paiement), Login/Register, ClubDashboard (infos/inscriptions/reçues/abonnement/communication), AdminPanel, MyEnrollments.

## Implémenté (2026-07-13)
- ✅ Modèle données + auth multi-rôles JWT (Phase 1)
- ✅ Import clubs 31 + recherche publique + fiches (Phase 2)
- ✅ Espace club : revendication, gestion page, créneaux/licenciés (Phase 3)
- ✅ Inscriptions + paiement (MOCK) + e-mails (MOCK) (Phase 4)
- ✅ Abonnement paliers + tableau de bord + communications (Phase 5)
- ✅ Modération admin des revendications (Phase 6 partiel)
- Tests : 35/35 backend, tous flux frontend OK.

## Backlog
- **P0** : brancher Stripe réel (abonnement clubs + inscriptions) ; e-mail transactionnel réel (Resend/SendGrid).
- **P1** : carte interactive Leaflet/tuiles réelles ; upload logos/photos (Object Storage) ; recherche par distance/géoloc navigateur ; bornes/prix paliers configurables.
- **P2** : import complet des 6927 équipements + enrichissement ; filtres avancés (niveau, jour) ; mobile natif ; mesure pilote (taux d'activation, inscriptions en ligne).

## Comptes test
- Admin : admin@sportconnect.fr / Admin31!
- Club : club@sportconnect.fr / Club31!
