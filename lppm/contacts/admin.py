from django.contrib import admin
from contacts.models import User, Contact, Proposal


class ProposalAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'members', 'type', 'file')
    list_filter = ('name', 'leader', 'members', 'type')
    search_fields = ('name', 'leader', 'members', 'type')

# Register your models here.
admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Proposal, ProposalAdmin)