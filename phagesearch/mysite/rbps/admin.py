from django.contrib import admin
from .models import Species,Proteins,Sequences
# Register your models here.

admin.site.register(Species)
admin.site.register(Proteins)
admin.site.register(Sequences)