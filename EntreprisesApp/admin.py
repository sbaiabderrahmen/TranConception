from django.contrib import admin
from .models import Entreprise
from .models import Utilisateur
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active','created_at')
    list_filter = ('role', 'is_active')
    readonly_fields = ('user_id', 'created_at', 'updated_at')

class entrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale','matricule_fiscal', 'type_entreprise', 'created_at')

admin.site.register(Entreprise, entrepriseAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)