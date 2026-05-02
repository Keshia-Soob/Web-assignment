from django.urls import path
from . import views as api_views

urlpatterns = [
    path("auth/login/",    api_views.api_login,    name="api_login"),
    path("auth/register/", api_views.api_register, name="api_register"),
    path("auth/logout/",   api_views.api_logout,   name="api_logout"),
    path("menu/",              api_views.api_menu_list,   name="api_menu_list"),
    path("menu/<int:item_id>/", api_views.api_menu_detail, name="api_menu_detail"),
    path("menu/nearby/",       api_views.api_menu_nearby, name="api_menu_nearby"),
    path("cart/",        api_views.api_cart_view,   name="api_cart_view"),
    path("cart/add/",    api_views.api_cart_add,    name="api_cart_add"),
    path("cart/remove/", api_views.api_cart_remove, name="api_cart_remove"),
    path("orders/",                        api_views.api_order_list,   name="api_order_list"),
    path("orders/place/",                  api_views.api_place_order,  name="api_place_order"),
    path("orders/<int:order_id>/status/",  api_views.api_order_status, name="api_order_status"),
    path("cooks/", api_views.api_cooks_list, name="api_cooks_list"),
    path("reviews/",        api_views.api_reviews_list,   name="api_reviews_list"),
    path("reviews/create/", api_views.api_reviews_create, name="api_reviews_create"),
    path("location/update/", api_views.api_location_update, name="api_location_update"),
    path("homecook/items/",                   api_views.api_homecook_items,  name="api_homecook_items"),
    path("homecook/accept/<int:item_id>/",    api_views.api_accept_item,     name="api_accept_item"),
    path("homecook/ready/<int:item_id>/",     api_views.api_mark_ready,      name="api_mark_ready"),
    path("homecook/delivered/<int:item_id>/", api_views.api_mark_delivered,  name="api_mark_delivered"),
]