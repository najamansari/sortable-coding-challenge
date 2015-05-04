"""Solution to Sortable's Coding Challenge (http://sortable.com/challenge/).
"""

import re
from codecs import open
import simplejson
from fuzzywuzzy import fuzz

__author__ = "Najam Ahmed Ansari"
__email__ = "najam.ansari@acit.com"

PRODUCTS = "products.txt"
LISTINGS = "listings.txt"
RESULTS = "results-python.txt"
UNMATCHED = "unmatched.txt"

pattern = re.compile('[\W_]+')
listings_tmp = []
results = []

with open(LISTINGS, "r", encoding='utf-8') as listings:
    for listing in listings:
        listings_tmp.append(simplejson.loads(listing.strip()))

with open(PRODUCTS, "r", encoding='utf-8') as products:
    with open(RESULTS, "w", encoding='utf-8') as results_file:
        for product in products:
            product = simplejson.loads(product.strip())
            temp = {
                "product_name": product.get("product_name"),
                "listings": []
            }
            model = pattern.sub('', product.get("model"))
            regex = re.compile(r"\b({})\b".format(model))
            for index, listing in enumerate(listings_tmp):
                if product.get("manufacturer").lower() !=\
                        listing.get("manufacturer").lower():
                    ratio = fuzz.ratio(
                        product.get("manufacturer"),
                        listing.get("manufacturer")
                    )
                    if ratio < 50:
                        continue
                title = pattern.sub('', listing.get("title"))
                if not regex.search(listing.get("title")) and not\
                        regex.search(title):
                    if fuzz.partial_ratio(model, title) < 90:
                        continue
                temp["listings"].append(listings_tmp.pop(index))
            if temp["listings"]:
                results_file.write(
                    "%s\n" % simplejson.dumps(temp, ensure_ascii=False)
                )
