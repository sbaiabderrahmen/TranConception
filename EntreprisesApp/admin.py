from django.contrib import admin
from .models import Entreprise
from .models import Utilisateur
from django.contrib.auth.admin import UserAdmin

admin.site.site_header = 'TransConnect -Administration'
admin.site.site_title = 'TransConnect'
# Register your models here.

class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active','created_at')
    list_filter = ('role', 'is_active')
    readonly_fields = ('user_id', 'created_at', 'updated_at')

class entrepriseAdmin(admin.ModelAdmin):
    search_fields = ('raison_sociale', 'matricule_fiscal','gerant__username','gerant__email')
    list_display = ('raison_sociale','matricule_fiscal', 'type_entreprise', 'created_at')

admin.site.register(Entreprise, entrepriseAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)