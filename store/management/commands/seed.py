from django.core.management.base import BaseCommand

from store.models import BlogPost, Product


PRODUCTS = [
    ("Leriya Fashion", "Leriya Fashion Striped Relaxed Casual Printed Shirt", 799, "img/product/f1.jpg", "Shirt", "Rayon all-over print, relaxed fit, short sleeve spread collar. Made in India.", True, False),
    ("Look Mark", "LookMark Men's Cotton Blend Printed Half Sleeve Shirt", 999, "img/product/f2.jpg", "Shirt", "Cotton blend regular fit shirt with stitched print and half sleeves.", True, False),
    ("Bullmer", "BULLMER Trendy Regular Fit Printed Casual Shirt", 1299, "img/product/f3.jpg", "Shirt", "Trendy regular fit printed casual shirt for everyday wear.", True, False),
    ("Lymio", "Lymio Casual Stylish Printed Shirt (Patta)", 1499, "img/product/f4.jpg", "Shirt", "Men stylish printed shirt with a relaxed everyday cut.", True, False),
    ("GRECIILOOKS", "GRECIILOOKS Loose Fit Cotton Cargo Jeans", 1599, "img/product/f5.jpg", "Jeans", "Baggy cargo jeans in cotton with a loose comfortable fit.", True, False),
    ("Lymio", "Lymio Men Denim Baggy Jeans", 1799, "img/product/f6.jpg", "Jeans", "Denim baggy jeans for men with a modern street look.", True, False),
    ("Ben Martin", "Ben Martin Loose Fit Denim Jeans", 1999, "img/product/f7.jpg", "Jeans", "Loose fit denim jeans designed for all-day comfort.", True, False),
    ("Noble Monk", "Noble Monk Baggy Fit Stretch Cargo Jeans", 2499, "img/product/f8.jpg", "Jeans", "Baggy cargo denim with stretch fabric and utility pockets.", True, False),
    ("CANALI", "CANALI Double Wool and Cashmere Blouson", 249999, "img/product/n1.jpg", "Jacket", "Luxury wool and cashmere blouson from the Canali main line.", False, True),
    ("KENZO", "KENZO Cloud Tiger Print Oversized T-Shirt", 22999, "img/product/n2.jpg", "T-Shirt", "Oversized cotton crew-neck with Cloud Tiger print.", False, True),
    ("VERSACE", "VERSACE Crystal Medusa T-Shirt", 64999, "img/product/n3.jpg", "T-Shirt", "Signature Medusa crystal detail on a luxury cotton tee.", False, True),
    ("GIORGIO ARMANI", "GIORGIO ARMANI Regular Fit Polo T-Shirt", 19999, "img/product/n4.jpg", "T-Shirt", "Blended regular fit polo from the Giorgio Armani main line.", False, True),
    ("AMIRI", "AMIRI Varsity Logo Distressed Straight Jeans", 69999, "img/product/n5.jpg", "Jeans", "Straight fit distressed jeans with varsity logo repair details.", False, True),
    ("DSQUARED2", "DSQUARED2 Lightly Washed Distressed Slim Jeans", 49999, "img/product/n6.jpg", "Jeans", "Slim fit jeans with a light wash and distressed finish.", False, True),
    ("VERSACE", "VERSACE Frayed Regular Fit Jeans", 39999, "img/product/n7.jpg", "Jeans", "Regular fit jeans with a frayed designer finish.", False, True),
    ("EMPORIO ARMANI", "EMPORIO ARMANI 5 Pocket J06 Pants", 18999, "img/product/n8.jpg", "Jeans", "Classic five-pocket J06 pants from Emporio Armani.", False, True),
]

POSTS = [
    ("The Cotton-Jersey Zip-Up Hoodie", "Kickstarter man braid gadard coloring book. Raclette waistcoat selfies yr wolf chartreuse hesagon irony, gadard...", "img/blog/img/img1.jpg", "13/01"),
    ("How to Style a Quiff", "Iusto necessitatibus quisquam doloremque sit ducimus sed odio repudiandae corporis quas sapiente...", "img/blog/img/img2.jpg", "13/01"),
    ("Must-Have Skater Boys Items", "Laboriosam aliquid ipsam numquam necessitatibus magni quos hic, et velit odit voluptas nemo enim amet dolorum...", "img/blog/img/img3.jpg", "13/01"),
    ("Runway-Inspired Trends", "Saepe voluptatum quaerat a voluptatibus, eaque delectus voluptas accusamus. Cum corrupti dolor velit suscipit...", "img/blog/img/img4.jpg", "13/01"),
    ("AW20 Menswear Trends", "Nam explicabo vitae culpa id, expedita hic et natus, provident temporibus quo corrupti dolorem quos...", "img/blog/img/img5.jpg", "13/01"),
]


class Command(BaseCommand):
    help = "Load demo products and blog posts."

    def handle(self, *args, **options):
        if not Product.objects.exists():
            Product.objects.bulk_create(
                [
                    Product(
                        brand=b,
                        name=n,
                        price=p,
                        image=img,
                        category=cat,
                        description=desc,
                        featured=feat,
                        new_arrival=new,
                    )
                    for b, n, p, img, cat, desc, feat, new in PRODUCTS
                ]
            )
            self.stdout.write(self.style.SUCCESS(f"Created {len(PRODUCTS)} products"))
        else:
            self.stdout.write("Products already exist")

        updated_prices = 0
        for brand, name, price, *_ in PRODUCTS:
            updated_prices += Product.objects.filter(brand=brand, name=name).update(price=price)
        if updated_prices:
            self.stdout.write(self.style.SUCCESS(f"Updated INR prices for {updated_prices} products"))

        if not BlogPost.objects.exists():
            BlogPost.objects.bulk_create(
                [
                    BlogPost(title=t, excerpt=e, image=img, posted_on=d)
                    for t, e, img, d in POSTS
                ]
            )
            self.stdout.write(self.style.SUCCESS(f"Created {len(POSTS)} blog posts"))
