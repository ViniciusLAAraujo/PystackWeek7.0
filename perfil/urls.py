from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.home, name= "home"),
    path('gerenciar/', views.gerenciar, name="gerenciar"),
    path('cadatrar_banco', views.cadastrar_banco, name='cadastrar_banco'),
    path('deletar_banco/<int:id>', views.deletar_banco, name="deletar_banco"),
    path('deletar_categoria/<int:id>', views.deletar_categoria, name="deletar_categoria"),
    path('cadastrar_categoria/', views.cadastrar_categoria, name="cadastrar_categoria"),
    path('update_categoria/<int:id>', views.update_categoria, name="update_categoria"),
]