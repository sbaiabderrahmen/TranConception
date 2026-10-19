from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from EntreprisesApp.models import Entreprise

STATUT_CHOICES = [
    ("publiee", "Publiée"),
    ("attribuee", "Attribuée"),
    ("en_cours", "En cours"),
    ("livree", "Livrée"),
    ("annulee", "Annulée"),
]


class Expedition(models.Model):
    reference = models.CharField(max_length=12, unique=True, editable=False)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), "Le poids doit être supérieur à 0.")],
    )
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="publiee")
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="expeditions",
        limit_choices_to={"type_entreprise": "chargeur"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} : {self.ville_depart} -> {self.ville_arrivee}"

    @classmethod
    def _generate_reference(cls):
        """Format EXP-AA-NNNNN : compteur 00001..99999, remis à zéro chaque année."""
        prefix = f"EXP-{timezone.now().strftime('%y')}-"
        derniere = (
            cls.objects.filter(reference__startswith=prefix)
            .order_by("-reference")
            .first()
        )
        compteur = int(derniere.reference[-5:]) + 1 if derniere else 1
        if compteur > 99999:
            raise ValidationError("Limite annuelle de 99999 expéditions atteinte.")
        return f"{prefix}{compteur:05d}"

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != "chargeur":
            raise ValidationError(
                {"entreprise": "L'entreprise associée à l'expédition doit être de type chargeur."}
            )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.reference}"