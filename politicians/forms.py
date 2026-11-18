from datetime import date

from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Party, Politician, Position, TermOfOffice

MAX_PHOTO_BYTES = 2 * 1024 * 1024
MAX_TERM_YEARS = 6


class PoliticianForm(forms.ModelForm):
    new_party = forms.CharField(
        label='Or add a new party', max_length=100, required=False,
        help_text='Leave both party fields blank for an independent.',
    )
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(), empty_label='Select a position',
    )
    term_start_year = forms.IntegerField(label='Term start year', min_value=1900, max_value=2100)
    term_end_year = forms.IntegerField(label='Term end year', min_value=1900, max_value=2100)

    field_order = [
        'first_name', 'last_name', 'position', 'term_start_year', 'term_end_year',
        'party', 'new_party', 'birth_date', 'biography', 'photo',
    ]

    class Meta:
        model = Politician
        fields = ['first_name', 'last_name', 'party', 'birth_date', 'biography', 'photo']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'biography': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['party'].empty_label = 'None (independent)'
        self.fields['party'].required = False
        self.fields['photo'].required = False
        term = self.instance.current_term if self.instance.pk else None
        if term:
            self.fields['position'].initial = term.position_id
            self.fields['term_start_year'].initial = term.start_year
            self.fields['term_end_year'].initial = term.end_year

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date >= date.today():
            raise forms.ValidationError('Birth date must be in the past.')
        return birth_date

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_BYTES:
            raise forms.ValidationError('Photo must be 2 MB or smaller.')
        return photo

    def clean(self):
        cleaned = super().clean()

        party = cleaned.get('party')
        new_party = (cleaned.get('new_party') or '').strip()
        cleaned['new_party'] = new_party
        if party and new_party:
            self.add_error('new_party', 'Choose an existing party or add a new one, not both.')

        start = cleaned.get('term_start_year')
        end = cleaned.get('term_end_year')
        if start and end:
            if end < start:
                self.add_error('term_end_year', 'End year cannot be before the start year.')
            elif end - start > MAX_TERM_YEARS:
                self.add_error('term_end_year', f'A term cannot be longer than {MAX_TERM_YEARS} years.')

        first = cleaned.get('first_name')
        last = cleaned.get('last_name')
        birth = cleaned.get('birth_date')
        if first and last and birth:
            duplicate = Politician.objects.filter(
                first_name__iexact=first, last_name__iexact=last, birth_date=birth,
            ).exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError(
                    'A politician with this name and birth date already exists.'
                )
        return cleaned

    def save(self, commit=True):
        politician = super().save(commit=False)

        new_party = self.cleaned_data.get('new_party')
        if new_party:
            politician.party = (
                Party.objects.filter(name__iexact=new_party).first()
                or Party.objects.create(name=new_party)
            )
        politician.save()

        term = politician.current_term
        if term:
            term.position = self.cleaned_data['position']
            term.start_year = self.cleaned_data['term_start_year']
            term.end_year = self.cleaned_data['term_end_year']
            term.save()
        else:
            TermOfOffice.objects.create(
                politician=politician,
                position=self.cleaned_data['position'],
                start_year=self.cleaned_data['term_start_year'],
                end_year=self.cleaned_data['term_end_year'],
            )
        return politician