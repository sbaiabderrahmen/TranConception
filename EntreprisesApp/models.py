from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
def validate_email(value):
    if not value:
        raise ValidationError("L'email est requis.")
    if not value.endswith('@gmail.com'):
        raise ValidationError("domaine invalide.")
# Create your models here.

class Utilisateur(AbstractUser):
    USER_id = models.CharField(primary_key=True, max_length=8, editable=False)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('administrateur', 'Administrateur'),
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
        ],
        default='chargeur',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 

class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200, null=False, blank=False)
    matricule_fiscale = models.CharField(max_length=17, null=False, blank=False,unique=True,primary_key=True)
   
    matricule_fiscal_validator = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message=(
        "Format attendu : 7 chiffres, 1 lettre (clé de contrôle), "
        "1 lettre (A/B/D/N/P/E), 1 lettre (M/P/C/N/E), 3 chiffres "
        "(ex. 1234567AAM000 ou 1234567-A-A-M-000)."
    )
)
    adresse = models.TextField(validators=[MinLengthValidator(20), "Adresse doit contenir au moins 20 caractères"]) 
    type_entreprise = models.CharField(max_length=100, choices=[('chargeur', 'Chargeur'), ('transporteur', 'Transporteur')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')
    
