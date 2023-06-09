# Generated by Django 4.2.2 on 2023-06-06 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('priceapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='наушники', max_length=30, verbose_name='название категории')),
            ],
            options={
                'verbose_name': 'категория товара',
                'verbose_name_plural': 'категории товаров',
                'ordering': ('name',),
            },
        ),
    ]