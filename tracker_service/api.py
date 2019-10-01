import os
import json
import string
import datetime
from tracker_service.users import User, UserResponse
import tracker_service.utils as utils
import boto3
from boto3.dynamodb.conditions import Key, Attr
import bcrypt
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from typing import List, Dict, Any
from dataclasses import dataclass, field


# Create the logger for this module
logger = utils.create_logger(__name__)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TRACKER_TABLE_NAME'])

'''Create a Flask App'''
app = Flask(__name__)
app.json_encoder = utils.DecimalEncoder
CORS(app)

# Setting JWT Settings
# app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_SECRET_KEY'] = 'aIQOrIk5a110FCeMZdfNo7BwXuAwgtAW'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)


@dataclass
class APIResponse:
    status: str
    result: Dict[str, Any] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)


@app.route('/users/create', methods=['POST'])
def create_user():
    logger.info('Create User')
    user = request.json

    # Hash password
    hashed_password = bcrypt.hashpw(user['password'].encode("utf-8"), salt=bcrypt.gensalt())
    user['password'] = hashed_password.decode('utf-8')
    username = user['username']

    response = table.get_item(Key={"partition_key": f"user_{username}", 'sort_key': username})

    if 'Item' in response:
        return {'message': 'Username already exists'}, 403
    else:
        result = table.put_item(Item={"partition_key": f"user_{username}", "sort_key": username, "payload": user})
        return {'message': 'User successfully created'}, 201


@app.route('/users/authenticate', methods=['POST'])
def authenticate_user():
    user = request.json
    username = user['username']
    is_valid_password = False

    try:
        record = table.get_item(Key={"partition_key": f"user_{username}", 'sort_key': username})
        if 'Item' in record:
            stored_password = record['Item']['payload']['password']
            supplied_password = user['password'].encode('utf-8')
            is_valid_password = bcrypt.checkpw(supplied_password, stored_password.encode('utf-8'))

        if is_valid_password:
            print('valid password')
            access_token = create_access_token(identity=username, fresh=True)
            refresh_token = create_refresh_token(username)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200

        if not is_valid_password:
            logger.info(f'Auth failure: username: {username}')
            return {}, 401

    except Exception as error:
        return {'error': str(error)}, 500


@app.route('/users/user', methods=['GET'])
@jwt_required
def get_user():

    user = get_jwt_identity()
    logger.info(f'Get User: {user}')

    user_record = table.get_item(Key={"partition_key": f"user_{user}", 'sort_key': user})

    if 'Item' in user_record:
        user = user_record['Item']
        userdata = user['payload']

        if 'password' in userdata:
            del userdata['password']

        return user, 200
    else:
        return {}, 404


@app.route('/users/pld', methods=['POST'])
@jwt_required
def update_pld_list():
    current_user = get_jwt_identity()
    plds = request.json

    update = table.update_item(Key={'partition_key': f"user_{current_user}", 'sort_key': current_user,},
                      UpdateExpression="SET #payload.#plds = :val",
                      ExpressionAttributeNames={
                          '#payload': 'payload',
                          '#plds': 'plds'
                      },
                      ExpressionAttributeValues={
                          ':val': plds,
                      },)
    print(f'Update Response: {update}')
    return {}, 200


@app.route('/products/active', methods=['GET'])
def get_active_plds_from_users():
    plds = []
    result = table.scan(ProjectionExpression='payload.plds')

    for i in result['Items']:
        if 'payload' in i:
            if len(i['payload']['plds']) > 0:
                for j in i['payload']['plds']:
                    if j['active'] == 'true' and j['pldcode'] not in plds:
                        plds.append(j['pldcode'])

    return jsonify(plds), 200


@app.route('/users/protected-path-test', methods=['GET'])
@jwt_required
def protected_test():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
    }), 401
