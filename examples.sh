# example commands to run
curl -X GET localhost:5000/cheeses
curl -X POST localhost:5000/cheeses --data @examples/cheddar.json

curl -X PUT localhost:5000/cheeses/5bbe44d7f6d76d0366238fbc -v --data '{"name":"cheddarinioII","type":"english cheddar","valid_through":"2008/09/31","weight":"100g"}' -H 'If-Match:63ff8e75-abcd-4e05-a6d0-cfb0ee26a44e'
curl -X GET localhost:5000/cheeses/5bbe44d7f6d76d0366238fbc
curl -X DELETE localhost:5000/cheeses/5bbe44d7f6d76d0366238fbc

curl -X POST localhost:5000/zones --data @examples/ageing_zone.json
curl -X POST localhost:5000/zones --data @examples/molding_zone.json

curl -X GET localhost:5000/zone-assignments
curl -X POST localhost:5000/zone-assignments/5bbe8f24f6d76d171a21b79f --data @examples/zone_assignment.json

curl -X GET localhost:5000/zones/5bbe9259f6d76d18e4fc853a/cheeses

curl -X POST localhost:5000/zone-transfers --data @examples/zone_transfer.json