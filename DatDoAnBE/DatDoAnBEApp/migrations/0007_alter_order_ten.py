# Generated by Django 5.0.1 on 2024-02-12 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DatDoAnBEApp', '0006_rename_user_dish_usershop_rename_user_menu_usershop_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ten',
            field=models.CharField(default='Hoa Don<django.db.models.fields.DateTimeField>', max_length=50),
        ),
    ]
