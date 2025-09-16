Web-Assignment KiPouCuit

Folder arrangement:

KiPouCuit/
│── manage.py
│── kipoucuit/                # Project settings
│   ├── _init_.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
    ├── templates/KiPouCuit/
│
├── users/                    # App 1: Users
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/users/
│
├── meals/                    # App 2: Meals
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/meals/
│
├── orders/                   # App 3: Orders
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/orders/
│
├── reviews/                  # App 4: Reviews
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/reviews/
│
├── adminpanel/               # App 5: Admin-specific logic
│   ├── views.py
│   ├── urls.py
│   ├── templates/adminpanel/
│
└── analytics/ (optional)
