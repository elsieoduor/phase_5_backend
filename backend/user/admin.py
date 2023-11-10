from django.contrib import admin
from .models import ChildrenOrphanage, Donation, Visit, Review, User
# Register your models here.

class ChildrenOrphanageAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'needs', 'visit')
    search_fields = ('name', 'location')
admin.site.register(ChildrenOrphanage, ChildrenOrphanageAdmin)

class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'children_orphanage', 'donated_item', 'date')
    search_fields = ('user__username', 'children_orphanage__name')
admin.site.register(Donation, DonationAdmin)

class VisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'children_orphanage', 'visit_date', 'completed')
    search_fields = ('user__username', 'children_orphanage__name')
    list_filter = ('completed', 'visit_date')
admin.site.register(Visit, VisitAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'children_orphanage', 'rating', 'date_reviewed')
    list_filter = ('rating', 'date_reviewed')
    search_fields = ('user__username', 'children_orphanage__name')
admin.site.register(Review, ReviewAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email')
admin.site.register(User, UserAdmin)