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

class Node:
  def __init__(self, data=""):
    self.data = data
    self.children = dict()

  def __str__(self):
    return self.data

  def insert(self, product_name, pos=0):
    curr_word = product_name[pos]
    if curr_word not in self.children:
      self.children[curr_word] = Node(curr_word)
    else:
      if pos == len(product_name) - 1:
        self.children[curr_word].data = curr_word
      else:
        self.children[curr_word].insert(product_name, pos+1)

class Trie:
  def __init__(self):
    self.root = Node()

  def insert(self, product_name):
    self.root.insert(product_name)

# all lowercase, alphanumeric
def process_product_name(name):
  return re.split('[W\_-]', name.lower())

# lowercase, alphanumeric, one space in between each word
def process_listing_title(title):
  processed = re.split('[W\s_-]', title.lower())
  return [word for word in processed if word != '']

def main():
  f = open("./listings.txt", encoding="utf-8")
  listings = [json.loads(line) for line in f]
  f.close()

  f = open("./products.txt", encoding="utf-8")
  products = [json.loads(line) for line in f]
  f.close()

  # will compare listings against this trie
  product_trie = Trie()
  for p in products:
    product_trie.insert(process_product_name(p["product_name"]))

  # preparing listings product names
  processed_listings = listings
  for l in processed_listings:
    print(process_listing_title(l["title"]))
    # l["title"] = process_name(l["title"])

if __name__ == "__main__":
  main()
