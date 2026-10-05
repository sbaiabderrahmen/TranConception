from django.db import models
from EntreprisesApp.models import Entreprise
from django.core.validators import MinValueValidator
# Create your models here.

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=11, unique=True,blank=False,null=False)
    type = models.CharField(max_length=20, choices=[
     ('camionnette', 'Camionnette'),
        ('fourgon', 'Fourgon'),
        ('camion_porteur', 'Camion_Porteur'),
        ('semi-remorque', 'Semi-Remorque')],)
    capacite= models.PositiveIntegerField(validators=[models.MinValueValidator(1), "Capacité doit être supérieure à 0 kilogrammes"])
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
     
entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='vehicules',limit_choices_to={'type_entreprise': 'transporteur'}
    )


