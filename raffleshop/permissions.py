from django.contrib.auth.models import Permission


class BrandSpecificPermission(Permission):
    class Meta:
        proxy = True
        verbose_name = "Brand-specific Permission"
        verbose_name_plural = "Brand-specific Permissions"
