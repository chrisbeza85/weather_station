# Generated by Django 5.1.1 on 2024-10-08 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0002_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='barcode_image',
            field=models.ImageField(blank=True, upload_to='barcodes/'),
        ),
    ]
