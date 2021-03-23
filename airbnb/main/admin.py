from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django.db import models
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPage, FlatPageAdmin


class CustomFlatPageAdmin(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': CKEditorUploadingWidget(),
        },
    }
    list_display = ('url',)


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, CustomFlatPageAdmin)




