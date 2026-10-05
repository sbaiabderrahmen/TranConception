    from django.db import models
    from EntreprisesApp.models import Entreprise
    import uuid
    from django.core.exceptions import ValidationError
    from django.utils import timezone


    class Expedition(models.Model):

        STATUT_CHOICES =[
            ('publiee', 'Publiée'),
            ('attribuee', 'Attribuée'),
            ('en_cours', 'En cours'),
            ('livree', 'Livrée'),
            ('annulee', ' Annulée'),
        
        ]

        reference = models.CharField(
            max_length=20,
            unique=True,
            editable=False
        )

        ville_depart = models.CharField(max_length=100,null=False, blank=False)

        ville_arrivee = models.CharField(max_length=100)

        poids_kg = models.DecimalField(
            max_digits=10,
            decimal_places=2
        )

        date_souhaitee = models.DateField()

        description = models.TextField(
            null=True,
            blank=True
        )

        statut = models.CharField(
            max_length=20,
            choices=STATUT_CHOICES,
            default='publiee'
        )

        entreprise = models.ForeignKey(
            Entreprise,
            on_delete=models.CASCADE,
            related_name='expeditions'
        )

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        def clean(self):
            super().clean()
            if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
                raise ValidationError("L'entreprise associée à l'expédition doit être de type 'chargeur'.") 
            
        def _generate_reference(cls):
        annee=timezone.now().strftime('%Y')
        dernier=cls.objects.filter(reference__startswith=f'EXP_{annee}').order_by('-reference').first()
        compteur = int(dernier.reference[-5:]) + 1 if dernier else 1
        if compteur > 99999:
            raise ValidationError("Limite exceeded") 
        return f"EXP_{annee}_{compteur:05d}"
        
        
        def save(self, *args, **kwargs):
            if not self.reference:
                self.reference = self._generate_reference()
            self.full_clean()
            super().save(*args, **kwargs)
            
