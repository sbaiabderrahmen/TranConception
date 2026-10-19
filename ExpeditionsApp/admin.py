from django.contrib import admin
from .models import Expedition
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_depart', 'date_arrivee', 'vehicule', 'offre')
# Register your models here.
admin.site.register(Expedition)