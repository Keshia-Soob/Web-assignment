GitHub Accounts:

KhushiR8 – Beedassy Nirvana Luxmi (2413850)
Rayyandl / Xeno003 – Rayyan Dialumsing (2413784)
Keshia-Soob – Soobrayen Keshia (2412920)
Bhaveshguptar1 – Bhavesh Guptar (2413494)
Haadiya04 – Haadiya Sana Begum Manreddy (2413050)
Nusayhah - Jalal-mohammad Bibi Nusayhah (2413912)

Web-Assignment KiPouCuit

Folder arrangement:

KiPouCuit/
│── manage.py
│
│── KiPouCuit/                     # Main project folder
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│
├── main_page/                     # App: Main Page
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/main_page/
│
├── meals/                         # App: Meals
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/meals/
│
├── orders/                        # App: Orders
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/orders/
│
├── reviews/                       # App: Reviews
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/reviews/
│
├── users/                         # App: Users (authentication, profiles)
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/users/
│
├── homecook/                      # App: Homecook
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/homecook/
│
├── static/
│
└── media/

How to populate menu:
Step1: Open terminal and go in KiPouCuit directory
Step2: Enter these command in the order below :-
              python manage.py makemigrations
              python manage.py migrate
              python manage.py dumpdata meals > meals_list.json
              python manage.py loaddata meals_list.json
