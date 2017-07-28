# match each listing to the correct product

'''
Product:
{
  "product_name": String // A unique id for the product
  "manufacturer": String
  "family": String // optional grouping of products
  "model": String
  "announced-date": String // ISO-8601 formatted date string, e.g. 2011-04-28T19:00:00.000-05:00
}

Listing:
{
  "title": String // description of product for sale
  "manufacturer": String // who manufactures the product for sale
  "currency": String // currency code, e.g. USD, CAD, GBP, etc.
  "price": String // price, e.g. 19.99, 100.00
}

return:
{
  "product_name": String
  "listings": Array[Listing]
}

* a single price listing may match at most one product
'''

import json
import re
from collections import defaultdict
from math import sqrt

class Product:
  def __init__(self, product_json):
    self.product_name = product_json["product_name"]
    self.manufacturer = alphanumeric_lower(product_json["manufacturer"])
    if "family" in product_json:
      self.family = alphanumeric_lower(product_json["family"])
    else:
      # set it as _none to give self.family some value
      self.family = "_none"
    self.model = alphanumeric_lower(product_json["model"])

  def __str__(self):
    return self.product_name

# 3 level deep nested dict
# 1: manufacturer
# 2: family
# 3: model
class Catalogue:
  def __init__(self):
    self.catalogue = {}
    self.match_results = defaultdict(list)

  # break down the catalogue into 3 levels
  def insert(self, product):
    manu = product.manufacturer
    family = product.family
    model = product.model
    if manu not in self.catalogue:
      self.catalogue[manu] = {}
    if family not in self.catalogue[manu]:
      self.catalogue[manu][family] = {}
    if model not in self.catalogue[manu][family]:
      self.catalogue[manu][family][model] = product

  # search space changes depending on which property we wanna match for
  # e.g. for manufacturer, obviously we can look at the manufacturer of the listing
  def search(self, search_space, level):
    for k,v in level.items():
      # "in" instead of "==" to match cases like Canon vs Canon Canada
      if k in search_space:
        return k
    return None

  def match(self, listing):
    title = listing["title"].lower()
    manu = listing["manufacturer"].lower()
    listing_words = [alphanumeric_lower(s) for s in title.split()]
    
    matched_manu = self.search(manu, self.catalogue)

    # just stop if no matched manufacturer
    if matched_manu != None:
      matched_family = self.search(title, self.catalogue[matched_manu])
      matched_model = None
      
      # listing may not have family info, but it always has model info,
      # so dont stop even if we dont find family
      if matched_family == None:

        # have to search every model for that manufacturer if no family info is given
        for family, models in self.catalogue[matched_manu].items():
          matched_model = self.search(listing_words, self.catalogue[matched_manu][family])
          if matched_model != None:
            matched_family = family
            break
      else:
        matched_model = self.search(listing_words, self.catalogue[matched_manu][matched_family])
    
      # add the listing to the match result if a matching model is found
      if matched_model != None:
        matched_product = self.catalogue[matched_manu][matched_family][matched_model]
        self.match_results[matched_product.product_name].append(listing)

def read_file(file_path):
  f = open(file_path, encoding="utf-8")
  content = [json.loads(line) for line in f]
  f.close()
  return content

def write_results(matches):
  result = {}
  f = open("results.txt", 'w')
  for product in matches:
    f.write(json.dumps(
      {
        "product_name": product,
        "listings": matches[product]
      }
    ))
    f.write('\n')
  f.close()
  print("Complete!")

# want to match something like SX130_IS to SX130IS
def alphanumeric_lower(s):
  stripped = re.sub('[^0-9a-zA-Z]+', '', s)
  return stripped.lower()

# only include listings within 2 SDs to filter out listings for parts, battery packs, etc
# basically only include listings with reasonable prices
def filter_sd(match_result):
  price_sum = 0
  for listing in match_result:
    price_sum += float(listing["price"])
  avg_sum = price_sum / len(match_result)

  diffs_sum = 0
  for listing in match_result:
    diffs_sum += (float(listing["price"]) - avg_sum) ** 2

  st_dev = sqrt(diffs_sum / len(match_result))
  lower = avg_sum - 2*st_dev
  upper = avg_sum + 2*st_dev
  return [l for l in match_result if lower <= float(l["price"]) and float(l["price"]) <= upper]

def main():
  listings = read_file("./listings.txt")
  products = read_file("./products.txt")

  catalogue = Catalogue()
  for product_json in products:
    product = Product(product_json)
    catalogue.insert(product)

  for listing in listings:
    catalogue.match(listing)

  for product in catalogue.match_results:
    catalogue.match_results[product] = filter_sd(catalogue.match_results[product])

  write_results(catalogue.match_results)

if __name__ == "__main__":
  main()
