# PurBeurre
Créez une plateforme pour amateurs de Nutella.

### Installation
1. Virtualenv & requirements.txt
```
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

2. Configuration de la base de données dans le settings.py

3. Faire les migrations
```
python manage.py makemigrations
python manage.py migrate
```

4. Lancer les tests
```
python manage.py test
```

5. Remplir la base de données
```
python manage.py add-level -l "low"
python manage.py add-level -l "moderate"
python manage.py add-level -l "high"

# add-product -n [nutriscore] -c [catégorie]
python manage.py add-product -n "a" -c "Desserts"
```
