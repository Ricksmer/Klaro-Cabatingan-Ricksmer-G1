from django.conf import settings
from django.db import models


class Party(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'parties'

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    rank = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return self.name


class Politician(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    party = models.ForeignKey(Party, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='politicians')
    birth_date = models.DateField()
    biography = models.TextField()
    photo = models.ImageField(upload_to='politician_photos/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name='politicians_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def current_term(self):
        terms = list(self.terms.all())  # uses prefetch cache when available
        return terms[0] if terms else None

    def __str__(self):
        return self.full_name


class TermOfOffice(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE, related_name='terms')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='terms')
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['-start_year']
        verbose_name_plural = 'terms of office'

    def __str__(self):
        return f'{self.politician} - {self.position} ({self.start_year}-{self.end_year})'