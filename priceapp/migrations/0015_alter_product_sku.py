# Generated by Django 4.2.2 on 2023-06-09 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('priceapp', '0014_missingproduct_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, help_text='IERM7.WW2', max_length=50, null=True, unique=True),
        ),
    ]
