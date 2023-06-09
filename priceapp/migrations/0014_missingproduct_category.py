# Generated by Django 4.2.2 on 2023-06-09 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('priceapp', '0013_missingproduct_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='missingproduct',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='priceapp.category', verbose_name='категория'),
        ),
    ]
