from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_razorpay_payment_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="razorpay_order_id",
        ),
        migrations.RemoveField(
            model_name="order",
            name="razorpay_payment_id",
        ),
        migrations.AlterField(
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
