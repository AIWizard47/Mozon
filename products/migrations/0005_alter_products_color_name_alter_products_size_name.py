# Generated by Django 5.0.6 on 2024-06-01 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_colorvariant_price_alter_sizevariant_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='color_name',
            field=models.ManyToManyField(blank=True, to='products.colorvariant'),
        ),
        migrations.AlterField(
            model_name='products',
            name='size_name',
            field=models.ManyToManyField(blank=True, to='products.sizevariant'),
        ),
    ]
