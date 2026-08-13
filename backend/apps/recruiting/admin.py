from django.contrib import admin

from apps.recruiting.models import Categoria, Postulacion, Puesto

admin.site.register(Puesto)
admin.site.register(Postulacion)
admin.site.register(Categoria)
