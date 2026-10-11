from django.contrib import admin

from .models import Attribute, Event, EventAttributeValue, EventStage, StageRole

admin.site.register(Event)
admin.site.register(EventStage)
admin.site.register(StageRole)
admin.site.register(Attribute)
admin.site.register(EventAttributeValue)

