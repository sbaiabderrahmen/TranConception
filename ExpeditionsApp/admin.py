from django.contrib import admin
from django.utils import timezone
from .models import Expedition
#Register your models here.
class EnRetardFilter(admin.SimpleListFilter):
    title = 'En retard'
    parameter_name = 'en_retard'
    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]
    def queryset(self, request, queryset):
        aujourd_hui = timezone.now().date()
        if self.value() == 'oui':
            return queryset.filter(statut='publiee', date_souhaitee__lt=aujourd_hui)
        if self.value() == 'non':
            return queryset.exclude(statut='publiee', date_souhaitee__lt=aujourd_hui)
        return queryset
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'entreprise')
    list_filter = ('statut', 'ville_depart', 'ville_arrivee', 'date_souhaitee', EnRetardFilter)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_select_related = ('entreprise',)
    list_editable = ('date_souhaitee',)
    ordering = ('date_souhaitee',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25
    readonly_fields = ('reference', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
        'fields': ('reference', 'entreprise', 'description')
        }),
        ('Itinéraire et poids', {
        'fields': ('ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee')
        }),
        ('Statut et horodatage', {
        'fields': ('statut', 'created_at', 'updated_at'),
        'classes': ('collapse',),
        }),
    )
admin.site.register(Expedition, ExpeditionAdmin)
from django.contrib import admin
from .models import Expedition
@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrivee', 'statut',
'date_souhaitee')
list_filter = ('statut', 'ville_depart')
search_fields = ('reference', 'entreprise__raison_sociale')
list_editable = ('statut',)
ordering = ('-created_at',)
date_hierarchy = 'date_souhaitee'
list_per_page = 25