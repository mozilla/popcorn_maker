from selectable.base import ModelLookup
from selectable.registry import registry

from users.models import Profile


class ProfileLookup(ModelLookup):
    model = Profile
    search_fields = (
        'name__icontains',
        'user__email__icontains',
    )

    def get_item_value(self, item):
        """Display for currently selected item"""
        return item.display_name

    def get_item_label(self, item):
        """Display for choice listings"""
        return item.display_name

    def get_queryset(self):
        qs = super(ProfileLookup, self).get_queryset()
        qs.order_by('name')
        return qs


registry.register(ProfileLookup)
