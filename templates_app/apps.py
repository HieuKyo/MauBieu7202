from django.apps import AppConfig


class TemplatesAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "templates_app"

    def ready(self):
        # Xóa khách hàng → xóa luôn ảnh chữ ký và ảnh CCCD của khách đó
        from django.db.models.signals import post_delete
        from .customer_cccd_images import delete_customer_cccd_images
        from .customer_signature import delete_customer_signatures
        from .models import Customer
        post_delete.connect(delete_customer_signatures, sender=Customer, dispatch_uid='delete_customer_signatures')
        post_delete.connect(delete_customer_cccd_images, sender=Customer, dispatch_uid='delete_customer_cccd_images')
