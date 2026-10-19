from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q

from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule

STATUT_CHOICES = [
    ("proposee", "Proposée"),
    ("acceptee", "Acceptée"),
    ("refusee", "Refusée"),
    ("retiree", "Retirée"),
]


class Offre(models.Model):
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), "Le prix doit être supérieur à 0.")],
    )
    delai_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Le délai doit être d'au moins 1 jour.")]
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="proposee")
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(
        Expedition, on_delete=models.CASCADE, related_name="offres"
    )
    transporteur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="offres",
        limit_choices_to={"type_entreprise": "transporteur"},
    )
    vehicule = models.ForeignKey(
        Vehicule, on_delete=models.CASCADE, related_name="offres"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Règle 4 aussi garantie au niveau base de données
            models.UniqueConstraint(
                fields=["expedition", "transporteur"],
                condition=Q(statut="proposee"),
                name="unique_offre_proposee_par_transporteur",
            ),
            models.UniqueConstraint(
                fields=["expedition"],
                condition=Q(statut="acceptee"),
                name="unique_offre_acceptee_par_expedition",
            ),
        ]

    def __str__(self):
        return f"Offre {self.pk} : {self.prix} DT / {self.delai_jours} j"

    def _statut_en_base(self):
        """Statut actuellement enregistré (None si l'offre n'existe pas encore)."""
        if not self.pk:
            return None
        return Offre.objects.filter(pk=self.pk).values_list("statut", flat=True).first()

    # ------------------------------------------------------------------
    # Règles métier (Part 2, section IV)
    # ------------------------------------------------------------------
    def clean(self):
        erreurs = {}
        creation = self._state.adding
        transporteur = self.transporteur if self.transporteur_id else None
        vehicule = self.vehicule if self.vehicule_id else None
        expedition = self.expedition if self.expedition_id else None

        # Règle 1 : seule une entreprise transporteur peut créer une offre
        if transporteur and transporteur.type_entreprise != "transporteur":
            erreurs["transporteur"] = "Une offre doit être créée par une entreprise transporteur."

        # Règle 2 : le véhicule appartient au transporteur de l'offre
        if vehicule and transporteur and vehicule.entreprise_id != transporteur.pk:
            erreurs["vehicule"] = "Ce véhicule n'appartient pas au transporteur de l'offre."

        if creation:
            # Règle 3 : nouvelles offres uniquement sur une expédition publiée
            if expedition and expedition.statut != "publiee":
                erreurs["expedition"] = "Cette expédition n'accepte plus de nouvelles offres."
            # Règle 6 : un véhicule indisponible ne peut pas être proposé sur une nouvelle offre
            if vehicule and not vehicule.disponible:
                erreurs["vehicule"] = "Ce véhicule n'est pas disponible."

        # Règle 7 : le gabarit du véhicule doit supporter le poids de l'expédition
        if vehicule and expedition and expedition.poids_kg > vehicule.charge_max_kg:
            erreurs.setdefault(
                "vehicule",
                f"Véhicule {vehicule.type_vehicule} : charge max {vehicule.charge_max_kg} kg, "
                f"expédition de {expedition.poids_kg} kg.",
            )

        # Règle 4 : pas deux offres 'proposee' du même transporteur sur la même expédition
        if self.statut == "proposee" and transporteur and expedition:
            doublon = Offre.objects.filter(
                expedition=expedition, transporteur=transporteur, statut="proposee"
            ).exclude(pk=self.pk)
            if doublon.exists():
                erreurs["__all__"] = "Ce transporteur a déjà une offre proposée sur cette expédition."

        # Acceptation : une seule offre acceptée, et seulement sur une expédition publiée
        if self.statut == "acceptee" and expedition:
            if self._statut_en_base() != "acceptee" and expedition.statut != "publiee":
                erreurs["__all__"] = "Seule une expédition publiée peut être attribuée."
            elif Offre.objects.filter(expedition=expedition, statut="acceptee").exclude(
                pk=self.pk
            ).exists():
                erreurs["__all__"] = "Une offre a déjà été acceptée pour cette expédition."

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        ancien_statut = self._statut_en_base()
        self.full_clean()

        with transaction.atomic():
            super().save(*args, **kwargs)

            # Règle 5 : cascade, uniquement au moment où l'offre PASSE à 'acceptee'
            if self.statut == "acceptee" and ancien_statut != "acceptee":
                self.expedition.statut = "attribuee"
                self.expedition.save()
                Offre.objects.filter(expedition=self.expedition, statut="proposee").exclude(
                    pk=self.pk
                ).update(statut="refusee")

    def accepter(self):
        self.statut = "acceptee"
        self.save()