from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from EntreprisesApp.models import Entreprise

TYPE_VEHICULE_CHOICES = [
    ("camionnette", "Camionnette / utilitaire léger"),
    ("fourgon", "Fourgon"),
    ("camion_porteur", "Camion porteur"),
    ("semi_remorque", "Semi-remorque"),
]

# Règle métier 7 : capacité maximale (kg) selon le gabarit (tableau Part 2, IV)
CHARGE_MAX_KG = {
    "camionnette": 1500,
    "fourgon": 3500,
    "camion_porteur": 19000,
    "semi_remorque": 26000,
}


class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=11, unique=True)
    type_vehicule = models.CharField(max_length=20, choices=TYPE_VEHICULE_CHOICES)
    capacite_kg = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "La capacité doit être supérieure à 0 kg.")]
    )
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="vehicules",
        limit_choices_to={"type_entreprise": "transporteur"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.immatriculation} ({self.type_vehicule})"

    @property
    def charge_max_kg(self):
        """Charge réellement transportable : min(capacité déclarée, plafond du gabarit)."""
        return min(self.capacite_kg, CHARGE_MAX_KG.get(self.type_vehicule, self.capacite_kg))

    def clean(self):
        # limit_choices_to ne filtre que les formulaires : la règle est vérifiée ici.
        if self.entreprise_id and self.entreprise.type_entreprise != "transporteur":
            raise ValidationError(
                {"entreprise": "Un véhicule doit appartenir à une entreprise de type transporteur."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)