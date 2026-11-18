from django.contrib import admin

from .models import Party, Politician, Position, TermOfOffice

admin.site.register(Party)
admin.site.register(Position)
admin.site.register(Politician)
admin.site.register(TermOfOffice)