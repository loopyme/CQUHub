# Generated by Django 2.2.3 on 2019-07-07 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0006_auto_20190707_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='create_topic',
            name='ifAnony',
            field=models.CharField(choices=[('不匿名', '不匿名'), ('匿名', '匿名')], max_length=50, verbose_name='是否匿名'),
        ),
    ]
