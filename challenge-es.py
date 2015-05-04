"""Solution to Sortable's Coding Challenge (http://sortable.com/challenge/).
"""

import argparse
from codecs import open
import simplejson
from elasticsearch import Elasticsearch

__author__ = "Najam Ahmed Ansari"
__email__ = "najam.ansari@acit.com"

PRODUCTS = "products.txt"
LISTINGS = "listings.txt"
RESULTS = "results-es.txt"

QUERY = """{
  "query": {
    "bool": {
      "must": [
        {
          "fuzzy": {
            "manufacturer": {
              "value": "%s",
              "max_expansions": "100"
            }
          }
        },
        {
          "query_string": {
            "default_field": "title",
            "query": "%s"
          }
        }
      ]
    }
  },
  "from": 0,
  "size": 25000
}
"""

DELETE_QUERY = '{"delete": {"_index": "%s", "_type": "json", "_id": %s}}'

parser = argparse.ArgumentParser(description='%s\n\n%s (%s)' % (
    __doc__, __author__, __email__
))
parser.add_argument('--index', dest='index', action="store_true",
                    help='Whether the listings should be indexed into ES')
parser.add_argument('--index', dest='index-name', default="sortable",
                    help='The name of the index that should be created in ES')
parser.add_argument('--host', dest='host', default="localhost",
                    help='The host-name/IP address of the ES server')
parser.add_argument('--port', dest='port', default=9200,
                    help='The port of the ES server')

parser.set_defaults(index=False)

all_arguments = parser.parse_known_args()
parsed_arguments = vars(all_arguments[0])

index_name = parsed_arguments["index-name"]

es = Elasticsearch(["http://%s:%s" % (parsed_arguments["host"],
                                      parsed_arguments["port"])])
es.indices.create(index=index_name, ignore=400)

if parsed_arguments['index']:
    index_id = 1
    with open(LISTINGS, "r", encoding='utf-8') as listings:
        for listing in listings:
            es.index(index="sortable", body=simplejson.loads(listing.strip()),
                     doc_type="json", id=index_id)
            index_id += 1

with open(PRODUCTS, "r", encoding='utf-8') as products:
    with open(RESULTS, "w", encoding='utf-8') as results_file:
        for product in products:
            product = simplejson.loads(product.strip())
            temp = {
                "product_name": product.get("product_name"),
                "listings": []
            }
            deletions = []
            model = product.get("model").replace(
                "/", "\\\\/"
            ).replace("!", "\\\\!")
            result = es.search(index=index_name, body=QUERY % (
                product.get("manufacturer"),
                model
            ))
            hits = result.get("hits", {})
            if hits.get("total", 0) and hits.get("max_score") > 2.0:
                for entry in hits.get("hits", []):
                    if entry.get("_score", 0) >= 2.0:
                        temp["listings"].append(entry.get("_source", {}))
                        deletions.append(
                            DELETE_QUERY % (index_name, entry.get("_id", 0))
                        )
            results_file.write(
                "%s\n" % simplejson.dumps(temp, ensure_ascii=False)
            )
            if deletions:
                es.bulk(deletions)
