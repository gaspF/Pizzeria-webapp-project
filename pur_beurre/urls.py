from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='pur-beurre-index'),
    path('results/', Results.as_view(), name='pur-beurre-results'),
    path('substitutes/<int:id>', Substitutes.as_view(), name='pur-beurre-substitutes'),
    path('food/<int:id>', Food.as_view(), name='pur-beurre-food'),
    path('save', SaveProduct.as_view(), name='pur-beurre-save'),
    path('legal_notices', Legal.as_view(), name='legal_notices'),
    path('saved_products/', login_required(views.UserSavedProductsList.as_view()), name='saved-products'),

]
