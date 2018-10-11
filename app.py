import uuid

import pymongo
from bson import ObjectId
from bson.json_util import dumps
from flask import Flask, request, jsonify

from schemas import (cheese_schema, zone_schema, zone_transfer_schema, 
                     zone_assignment_schema)
from validation import validate, validation_error
from validation.errors import (CHEESE_ASSIGNED, IF_MATCH_INVALID, IF_MATCH_MISSING,
                               ZONE_NOT_EXISTANT, ZONE_ERROR)

app = Flask(__name__)
mongo = pymongo.MongoClient()
fridge = mongo.fridge



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


@app.route('/zones', methods=['GET', 'POST'])
def zones_route():
    if request.method == 'POST':
        data = request.get_json(force=True)

        error = validate(data, zone_schema)
        if error is not None:
            return jsonify({'error': validation_error(error)}), 400

        data['version'] = uuid.uuid4()
        zone_id = fridge.zones.insert_one(data).inserted_id

        return jsonify({'_id': str(zone_id)}), 202
    else:  # GET
        zones = fridge.zones.find()

        zones = [{**zone, '_id': str(zone['_id'])} for zone in zones]
        return jsonify(zones), 200


@app.route('/zones/<_id>', methods=['GET', 'PUT', 'DELETE'])
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
    
    zone_cheeses = fridge.zone_assignments.find({'zone_id': _id})
    zone_cheeses = [{**cheese, '_id': str(cheese['_id'])} for cheese in zone_cheeses]
    return jsonify(zone_cheeses), 200


@app.route('/zone-assignments', methods=['GET'])
def zone_assignments_route():
    assignment = fridge.zone_assignment_requests.insert_one({}).inserted_id
    return jsonify({'request_id': str(assignment)}), 200


@app.route('/zone-assignments/<assignment_id>', methods=['POST'])
def zone_assignments_request_route(assignment_id):
    data = request.get_json(force=True)
    error = validate(data, zone_assignment_schema)
    if error is not None:
        return jsonify({'error': validation_error(error)}), 400

    cheese_id, zone_id = data['cheese_id'], data['zone_id']

    assignment = fridge.zone_assignment_requests.find_one({'_id': ObjectId(assignment_id)})
    if assignment is None:
        return jsonify({'error': "Not found"}), 404

    found_zone = fridge.zones.find_one({'_id': ObjectId(zone_id)})
    if found_zone is None:
        return jsonify({'error': ZONE_NOT_EXISTANT.format(zone_id)}), 400
    
    found_assignment = fridge.zone_assignments.find_one({'cheese_id': cheese_id})
    if found_assignment is not None:
        return jsonify({'error': CHEESE_ASSIGNED}), 400

    fridge.zone_assignments.insert_one(data)
    fridge.zone_assignment_requests.delete_one(assignment)
    
    return jsonify({'status': 'OK'}), 200


@app.route('/zone-transfers', methods=['POST'])
def zone_transfers_route():
    data = request.get_json(force=True)

    error = validate(data, zone_transfer_schema)
    if error is not None:
        print('Kappa 123')
        return jsonify({'error': validation_error(error)}), 400

    cheese_id, from_zone_id, to_zone_id = (data['cheese_id'], data['from_zone_id'],
                                           data['to_zone_id'])

    zone_assignment_to_delete = {'cheese_id': cheese_id, 'zone_id': from_zone_id}
    found = fridge.zone_assignments.find_one(zone_assignment_to_delete)

    if found is None:
        print('Kappa 123')
        return jsonify({'error': ZONE_ERROR.format(cheese_id, from_zone_id)}), 400
    
    fridge.zone_assignments.insert_one({'cheese_id': cheese_id, 'zone_id': to_zone_id})
    fridge.zone_assignments.delete_one(zone_assignment_to_delete)

    return jsonify({'status': 'OK'}), 200


if __name__ == '__main__':
    app.run()


