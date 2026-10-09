from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_order_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("cod", "Cash on Delivery"),
                    ("upi", "UPI"),
                    ("card", "Card"),
                ],
                default="cod",
                max_length=10,
            ),
        ),
    ]
