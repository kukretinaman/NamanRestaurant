from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_assign_default_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(
                to='customer.restaurant',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                null=False,   # now required
                blank=False,
            ),
        ),
    ]
