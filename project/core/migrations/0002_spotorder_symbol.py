# Generated by Django 3.2 on 2021-06-10 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_default_users_and_passwords'),
    ]

    operations = [
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10, unique=True)),
                ('price', models.DecimalField(blank=True, decimal_places=8, max_digits=18, null=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['symbol'],
            },
        ),
        migrations.CreateModel(
            name='SpotOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.BigIntegerField(unique=True)),
                ('client_order_id', models.CharField(max_length=100, unique=True)),
                ('price', models.DecimalField(decimal_places=8, max_digits=18)),
                ('executed_quantity', models.DecimalField(decimal_places=8, max_digits=18)),
                ('cummulative_quote_quantity', models.DecimalField(decimal_places=8, max_digits=18)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('PARTIALLY_FILLED', 'Partially filled'), ('FILLED', 'Filled'), ('CANCELED', 'Cancelled'), ('PENDING_CANCEL', 'Pending cancel'), ('REJECTED', 'Rejected'), ('EXPIRED', 'Expired')], max_length=50)),
                ('side', models.CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell')], max_length=5)),
                ('timestamp', models.BigIntegerField()),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='core.symbol')),
            ],
            options={
                'ordering': ['symbol'],
            },
        ),
    ]
