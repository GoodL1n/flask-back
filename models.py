from sqlalchemy import ForeignKey

from app import db
from passlib.hash import pbkdf2_sha256 as sha256

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(120), nullable = True)
    lastname = db.Column(db.String(120), nullable=True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    role = db.Column(db.String(120), nullable = True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)

class CustomerModel(db.Model):
    __tablename__ = "customer"

    customer_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.SmallInteger)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(50))
    address_id = db.Column(db.SmallInteger, ForeignKey('address.address_id'), nullable=False)
    activebool = db.Column(db.Boolean)
    create_date = db.Column(db.Date)
    last_update = db.Column(db.DateTime)
    active = db.Column(db.Integer)

    def add(self):
        db.session.add(self)
        db.session.commit()

class AddressModel(db.Model):
    __tablename__ = "address"

    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50))
    address2 = db.Column(db.String(50))
    district = db.Column(db.String(20))
    city_id = db.Column(db.SmallInteger, ForeignKey('city.city_id'), nullable=False)
    postal_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    last_update = db.Column(db.DateTime)

class CityModel(db.Model):
    __tablename__ = "city"

    city_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50))
    country_id = db.Column(db.SmallInteger, ForeignKey('country.country_id'), nullable=False)
    last_update = db.Column(db.DateTime)

class CountryModel(db.Model):
    __tablename__ = "country"

    country_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50))
    last_update = db.Column(db.DateTime)


