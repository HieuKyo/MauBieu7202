# Generated migration to add customer_classification to visible_field_groups

from django.db import migrations


def update_visible_field_groups(apps, schema_editor):
    """Add customer_classification to all categories' visible_field_groups"""
    Category = apps.get_model('templates_app', 'Category')

    for category in Category.objects.all():
        if category.visible_field_groups:
            # If visible_field_groups is already set and doesn't have customer_classification
            if 'customer_classification' not in category.visible_field_groups:
                # Find the right position (after employment, before banking)
                if 'employment' in category.visible_field_groups:
                    idx = category.visible_field_groups.index('employment') + 1
                    category.visible_field_groups.insert(idx, 'customer_classification')
                else:
                    # Just append if employment not found
                    category.visible_field_groups.append('customer_classification')
                category.save()


def reverse_update(apps, schema_editor):
    """Remove customer_classification from visible_field_groups"""
    Category = apps.get_model('templates_app', 'Category')

    for category in Category.objects.all():
        if category.visible_field_groups and 'customer_classification' in category.visible_field_groups:
            category.visible_field_groups.remove('customer_classification')
            category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0016_add_ten_the_2_field'),
    ]

    operations = [
        migrations.RunPython(update_visible_field_groups, reverse_update),
    ]
