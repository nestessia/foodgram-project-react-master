# Generated by Django 4.2.7 on 2023-12-16 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscribe',
            name='unique_subscription',
        ),
    ]
