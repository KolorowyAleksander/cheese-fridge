import uuid

import pymongo
from bson import ObjectId
from bson.json_util import dumps
from flask import Flask, request, jsonify

from schemas import cheese_schema, zone_schema
from validation import validate, validation_error


app = Flask(__name__)
mongo = pymongo.MongoClient()
fridge = mongo.fridge


IF_MATCH_MISSING = "Missing If-Match header when updating a resource"
IF_MATCH_INVALID = "If-Match header not matching current version"


@app.before_request
def before_request():
    if request.method == 'PUT' and request.headers.get('If-Match') is None:
        return jsonify({'error': IF_MATCH_MISSING }), 400


@app.route('/cheeses', methods=['GET', 'POST', 'DELETE'])
def cheese_route():
    if request.method == 'POST':
        data = request.get_json(force=True)

        error = validate(data, cheese_schema)
        if error is not None:
            return jsonify({'error': validation_error(error)}), 400

        data['version'] = uuid.uuid4()
        cheese_id = fridge.cheeses.insert_one(data).inserted_id

        return jsonify({'cheese_id': str(cheese_id)}), 202
    elif request.method == 'DELETE':
        fridge.cheeses.delete_many({})
        return jsonify({'status': 'OK'}), 200
    else:  # GET
        cheeses = fridge.cheeses.find()

        cheeses = [{**cheese, '_id': str(cheese['_id'])} for cheese in cheeses]
        return jsonify(cheeses), 200


@app.route('/cheeses/<_id>', methods=['GET', 'PUT', 'DELETE'])
def cheese_id_route(_id):
    if request.method == 'PUT':
        data = request.get_json(force=True)

        error = validate(data, cheese_schema)
        if error is not None:
            return jsonify({'error': validation_error(error)}), 400

        cheese = fridge.cheeses.find_one({'_id': ObjectId(_id)})
        if cheese is None:
            return jsonify({'error': "Not found"}), 404
        
        if cheese['version'] != request.headers.get('If-Match'):
            return jsonify({'error': IF_MATCH_INVALID}), 400

        data['version'] = str(uuid.uuid4())

        fridge.cheeses.replace_one({'_id': ObjectId(_id)}, data)

        return jsonify({'_id': str(cheese['_id'])}), 202, {'ETag': data['version']}
    elif request.method == 'DELETE':
        cheese = fridge.cheeses.find_one({'_id': ObjectId(_id)})
        if cheese is None:
            return jsonify({'error': "Not found"}), 404

        fridge.cheeses.delete_one({'_id': ObjectId(_id)})

        return jsonify({'status': 'OK'}), 200
    else:  # GET
        cheese = fridge.cheeses.find_one({'_id': ObjectId(_id)})
        if cheese is None:
            return jsonify({'error': "Not found"}), 404

        return (jsonify({**cheese, '_id': str(cheese['_id'])}), 
                200, {'ETag': cheese['version']})


@app.route('/zones')
def zones_route():
    if request.method == 'POST':
        data = request.get_json(force=True)

        error = validate(data, zone_schema)
        if error is not None:
            return jsonify({'error': validation_error(error)}), 400

        data['version'] = uuid.uuid4()
        data['cheeses'] = []
        zone_id = fridge.zones.insert_one(data).inserted_id

        return jsonify({'_id': str(zone_id)}), 202
    elif request.method == 'DELETE':
        fridge.zones.delete_many({})
        return jsonify({'status': 'OK'}), 200
    else:  # GET
        zones = fridge.zones.find()

        zones = [{**zone, '_id': str(zone['_id'])} for zone in zones]
        return jsonify(zones), 200


@app.route('/zones/<_id>', methods=['GET'])
def zones_id_route(_id):
    if request.method == 'PUT':
        data = request.get_json(force=True)

        error = validate(data, zone_schema)
        if error is not None:
            return jsonify({'error': validation_error(error)}), 400

        zone = fridge.zones.find_one({'_id': ObjectId(_id)})
        if zone is None:
            return jsonify({'error': "Not found"}), 404
        
        if zone['version'] != request.headers.get('If-Match'):
            return jsonify({'error': IF_MATCH_INVALID}), 400

        data['version'] = str(uuid.uuid4())

        fridge.zones.replace_one({'_id': ObjectId(_id)}, data)

        return jsonify({'_id': str(zone['_id'])}), 202, {'ETag': data['version']}
    elif request.method == 'DELETE':
        zone = fridge.zones.find_one({'_id': ObjectId(_id)})
        if zone is None:
            return jsonify({'error': "Not found"}), 404

        fridge.zones.delete_one({'_id': ObjectId(_id)})

        return jsonify({'status': 'OK'}), 200
    else:  # GET    
        zone = fridge.zones.find_one({'_id': ObjectId(_id)})
        if zone is None:
            return jsonify({'error': "Not found"}), 404

        return (jsonify({**zone, '_id': str(zone['_id'])}), 
                200, {'ETag': zone['version']})

@app.route('/zones/<_id>/cheeses', methods=['GET'])
def zones_id_cheeses_route(_id):
    zone = fridge.zones.find_one({'_id': ObjectId(_id)})
    if zone is None:
        return jsonify({'error': "Not found"}), 404
    
    cheeses_for_zone = fridge.zone_assignments.find({'zone_id': ObjectId(_id)})
    return dumps(cheeses_for_zone), 200


@app.route('/zone-assignments', methods=['GET'])
def zone_assignments_route():
    assignment = fridge.zone_assignment_requests.insert({})
    return jsonify({'request_id': str(assignment['_id'])}), 200


@app.route('/zone-assignments/<assignment_id>', methods=['POST'])
def zone_assignments_request_route(assignment_id):
    data = request.get_json(force=True)
    assignment = fridge.zone_assignment_requests.find_one({'_id': ObjectId(assignment_id)})
    if assignment is None:
        return jsonify({'error': "Not found"}), 404
    
    fridge.zone_assignment_requests.delete_one(assignment)
    fridge.zone_assignments.insert_one()



@app.route('/zone-transfers')
def zone_transfers_route():
    # from zone and to zone
    pass


if __name__ == '__main__':
    app.run()


