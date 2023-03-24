from flask import make_response, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from flask_restful import Resource, reqparse
from sqlalchemy import func

from app import db
from models import UserModel, RevokedTokenModel, CustomerModel, AddressModel, CityModel, CountryModel

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)
parser.add_argument('role', help='This field cannot be blank', required=False)

customers_parser = reqparse.RequestParser()
customers_parser.add_argument('customer_id', help='This field cannot be blank', required=True)
customers_parser.add_argument('first_name', help='This field cannot be blank', required=True)
customers_parser.add_argument('last_name', help='This field cannot be blank', required=True)
customers_parser.add_argument('email', help='This field cannot be blank', required=True)
customers_parser.add_argument('create_date', help='This field cannot be blank', required=True)

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password']),
            role=data['role']
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            return {'message': str(e)}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'id': current_user.id,
                'firstName': current_user.firstname,
                'lastName': current_user.lastname,
                'username': current_user.username,
                'role': current_user.role,
                'jwtToken': access_token,
                'jwtRefreshToken': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class AllCustomers(Resource):
    def put(self):
        data = customers_parser.parse_args()
        if CustomerModel.find_by_customer(data['customer_id']):
            query = db.session.query(CustomerModel
                                     ).filter(CustomerModel.customer_id == data['customer_id']
                                              ).update({
                'first_name' : data['first_name'],
                'last_name' : data['last_name'],
                'email' : data['email'],
                'create_date' : data['create_date']
            })
            db.session.commit()
            return jsonify(query)
        else:
            return {'message': 'Customer with id = {} bot exists'.format(data['customer_id'])}

    def get(self):
        def to_json(x):
            return {
                'customer_id': x.CustomerModel.customer_id,
                'store_id': x.CustomerModel.store_id,
                'first_name': x.CustomerModel.first_name,
                'last_name': x.CustomerModel.last_name,
                'email': x.CustomerModel.email,
                'address_id': x.CustomerModel.address_id,
                'activebool': x.CustomerModel.activebool,
                'create_date': str(x.CustomerModel.create_date),
                'active': x.CustomerModel.active
            }

        query = db.session.query(CustomerModel, AddressModel, CountryModel, CityModel
                                 ).filter(CustomerModel.address_id == AddressModel.address_id
                                          ).filter(AddressModel.city_id == CityModel.city_id
                                                   ).filter(CityModel.country_id == CountryModel.country_id)
        records = query.all()
        return jsonify(list(map(lambda x: to_json(x), records)))


class AllAddress(Resource):
    def get(self):
        try:
            def to_json(x):
                return {
                    'address_id': x.address_id,
                    'district': x.district,
                }

            query = db.session.query(AddressModel)
            records = query.all()
            return jsonify(list(map(lambda x: to_json(x), records)))
        except Exception as e:
            return {'Message': str(e)}


class AllCities(Resource):
    def get(self):
        try:
            def to_json(x):
                return {
                    'city_id': x.city_id,
                    'city': x.city,
                }

            query = db.session.query(CityModel)
            records = query.all()
            return jsonify(list(map(lambda x: to_json(x), records)))
        except Exception as e:
            return {'Message': str(e)}


class AllCountries(Resource):
    def get(self):
        try:
            def to_json(x):
                return {
                    'country_id': x.country_id,
                    'country': x.country,
                }

            query = db.session.query(CountryModel)
            records = query.all()
            return jsonify(list(map(lambda x: to_json(x), records)))
        except Exception as e:
            return {'Message': str(e)}

class SecretResource(Resource):
    @jwt_required()
    def get(self):
        data = [{'id': 12, 'uid': 32}]
        return jsonify(data)

class CountCities(Resource):
    def get(self):
        def to_json(x):
            return {
                'count': x.count,
                'country': x.country
            }

        query = db.session.query(func.count(CityModel.city).label('count'), CountryModel.country)
        query = query.join(CityModel, CityModel.country_id == CountryModel.country_id)
        query = query.group_by(CountryModel.country)\
            .order_by(CountryModel.country)
        records = query.all()

        print(records)
        return jsonify(list(map(lambda x: to_json(x), records)))