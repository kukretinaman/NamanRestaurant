from django.db import migrations

def assign_default_restaurant(apps, schema_editor):
    Restaurant = apps.get_model('customer', 'Restaurant')
    Order = apps.get_model('customer', 'Order')
    User = apps.get_model('auth', 'User')
    
    # Create a default user if it doesn't exist
    default_user, _ = User.objects.get_or_create(
        username='default_owner',
        defaults={'email': 'default@example.com'}
    )
    
    default_rest, _ = Restaurant.objects.get_or_create(
        name="Default Restaurant", 
        defaults={'owner': default_user}
    )
    Order.objects.filter(restaurant__isnull=True).update(restaurant=default_rest)

class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_alter_order_customer_alter_order_status_restaurant_and_more'),  # <-- make sure this points to the file that creates Restaurant
    ]

    operations = [
        migrations.RunPython(assign_default_restaurant),
    ]
