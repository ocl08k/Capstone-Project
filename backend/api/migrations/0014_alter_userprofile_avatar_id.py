# Generated by Django 5.1.1 on 2024-11-11 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_remove_userprogress_user_userprofile_avatar_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
