from django.contrib import admin

# Register your models here.
from .models import Claims, ClaimAuditable , Parameter , dsoutcome , LOB , policy , ClaimNotes


class ClaimAuditableAdmin(admin.ModelAdmin):
    list_display = ('claim','parameter_score_ai','total', 'met' , 'accuracy_denominator' , 'accuracy_numerator')

class dsoutcomeAdmin(admin.ModelAdmin):
    list_display = ('parameter_id','leakage_category')


admin.site.register(Claims)

admin.site.register(ClaimAuditable , ClaimAuditableAdmin)

admin.site.register(Parameter)

admin.site.register(dsoutcome, dsoutcomeAdmin)

admin.site.register(LOB)

admin.site.register(policy)

admin.site.register(ClaimNotes)