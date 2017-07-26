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
from collections import defaultdict

class Product:
  def __init__(self, product_json):
    self.product_name = product_json["product_name"]
    self.manufacturer = product_json["manufacturer"]
    if "family" in product_json:
      self.family = product_json["family"]
    else:
      self.family = "_none"
    self.model = product_json["model"]

  def __str__(self):
    return self.product_name

class Catalogue:
  def __init__(self):
    self.catalogue = {}
    self.match_results = defaultdict(list)

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

  def search(self, listing):
    title = listing["title"]
    manu = listing["manufacturer"]
    words = title.split()
    
    matched_manu = None
    for m in self.catalogue.keys():
      if m in manu:
        matched_manu = m
        break

    matched_family = None
    if matched_manu != None:
      for f in self.catalogue[matched_manu].keys():
        if f in title:
          matched_family = f
          break

    if matched_manu != None:
      if matched_family == None:
        for f in self.catalogue[matched_manu].keys():
          for mo in self.catalogue[matched_manu][f].keys():
            if mo in words:
              matched_product = self.catalogue[matched_manu][f][mo]
              self.match_results[matched_product.product_name].append(listing)
              break
      else:
        for mo in self.catalogue[matched_manu][matched_family].keys():
          if mo in words:
            matched_product = self.catalogue[matched_manu][matched_family][mo]
            self.match_results[matched_product.product_name].append(listing)
            break



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

def main():
  listings = read_file("./listings.txt")
  products = read_file("./products.txt")

  catalogue = Catalogue()
  for product_json in products:
    product = Product(product_json)
    catalogue.insert(product)
  
  for listing in listings:
    catalogue.search(listing)

  write_results(catalogue.match_results)  

if __name__ == "__main__":
  main()
