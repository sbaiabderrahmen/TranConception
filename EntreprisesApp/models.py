import re

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Validateurs
# ---------------------------------------------------------------------------
def validate_email_gmail(value):
    if not value:
        raise ValidationError("L'adresse email est obligatoire.")
    if not value.lower().endswith("@gmail.com"):
        raise ValidationError("Seuls les emails du domaine gmail.com sont acceptés.")


# Regex fournie par l'énoncé (Part 2, section III)
matricule_fiscal_validator = RegexValidator(
    regex=r"^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$",
    message=(
        "Format attendu : 7 chiffres, 1 lettre (clé de contrôle), "
        "1 lettre (A/B/D/N/P), 1 lettre (M/P/C/N/E), 3 chiffres."
    ),
)

ROLE_CHOICES = [
    ("chargeur", "Chargeur"),
    ("transporteur", "Transporteur"),
    ("admin", "Administrateur"),
]

TYPE_ENTREPRISE_CHOICES = [
    ("chargeur", "Chargeur"),
    ("transporteur", "Transporteur"),
]


# ---------------------------------------------------------------------------
# Utilisateur
# ---------------------------------------------------------------------------
class UtilisateurManager(UserManager):
    """UserManager personnalisé : le rôle est fixé selon le contexte d'inscription."""

    def create_chargeur(self, username, email=None, password=None, **extra_fields):
        extra_fields["role"] = "chargeur"
        return self.create_user(username, email, password, **extra_fields)

    def create_transporteur(self, username, email=None, password=None, **extra_fields):
        extra_fields["role"] = "transporteur"
        return self.create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields["role"] = "admin"
        return super().create_superuser(username, email, password, **extra_fields)


class Utilisateur(AbstractUser):
    user_id = models.CharField(max_length=8, primary_key=True, editable=False)
    email = models.EmailField(unique=True, validators=[validate_email_gmail])
    telephone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="chargeur")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UtilisateurManager()

    def __str__(self):
        return f"{self.user_id} - {self.username}"

    @classmethod
    def generer_user_id(cls):
        """Format AAuserNN : AA = 2 derniers chiffres de l'année, NN = 00..99 (remis à 0 chaque année)."""
        prefix = f"{timezone.now().strftime('%y')}user"
        dernier = (
            cls.objects.filter(user_id__startswith=prefix)
            .order_by("-user_id")
            .first()
        )
        compteur = int(dernier.user_id[-2:]) + 1 if dernier else 0
        if compteur > 99:
            raise ValidationError("Limite de 100 inscriptions atteinte pour cette année.")
        return f"{prefix}{compteur:02d}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.generer_user_id()
        self.full_clean(exclude=["password"])
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Entreprise
# ---------------------------------------------------------------------------
class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200)
    matricule_fiscal = models.CharField(
        max_length=17, unique=True, validators=[matricule_fiscal_validator]
    )
    type_entreprise = models.CharField(max_length=20, choices=TYPE_ENTREPRISE_CHOICES)
    adresse = models.TextField(
        validators=[MinLengthValidator(20, "L'adresse doit contenir au moins 20 caractères.")]
    )
    utilisateur = models.OneToOneField(
        Utilisateur, on_delete=models.CASCADE, related_name="entreprise"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.raison_sociale} ({self.type_entreprise})"

    def clean(self):
        # On stocke la forme canonique (13 caractères, sans séparateurs) pour que
        # "1234567/A/A/M/000" et "1234567AAM000" ne passent pas comme 2 matricules.
        if self.matricule_fiscal:
            self.matricule_fiscal = re.sub(r"[/ -]", "", self.matricule_fiscal).upper()
        if (
            self.utilisateur_id
            and self.type_entreprise
            and self.utilisateur.role != self.type_entreprise
        ):
            raise ValidationError(
                {"utilisateur": "Le rôle de l'utilisateur doit correspondre au type de l'entreprise."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)