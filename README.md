Déploiement de l'application sur Heroku:

Via Heroku CLI : 
- Cloner les documents du repository https://github.com/gaspF/OpenclassRooms---Parcours-Python---Projet-8 sur votre machine
- Se connecter à Heroku via la commande "Heroku login"
- Créer une nouvelle application via la commande "heroku create"
- Rajouter dans settings.py "ALLOWED_HOSTS" l'url correspondant au projet Heroku créé.
- Déterminer les variables d'environnement via la commande "heroku config:set" (SECRET_KEY, ENV=PRODUCTION, DB_USER, DB_PASS). DB_USER correspond au nom d'utilisateur de votre BDDR, DB_PASS au mot de passe associé.
- Add, commit et pusher l'application sur Heroku via les commandes "git add ." / "git commit -am "le commit"" / "git push heroku master".
- Créer un superuser sur Heroku via la commande "heroku run python manage.py createsuperuser" et renseigner les champs.
- Importer la base de données via la commande "heroku run python manage.py loaddata (...)/pur_beurre.json" (Le fichier dump fourni dans le repository github ou le votre)
