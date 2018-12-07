import responder
import graphene

from marshmallow import Schema, fields

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref

from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

engine = create_engine('sqlite:///database.sqlite3', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = responder.API(title="Web Service", version="1.0", openapi="3.0.0", docs_route="/docs")

class PetModel(Base):
    __tablename__ = 'pets'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Pet(SQLAlchemyObjectType):
    class Meta:
        model = PetModel
        interfaces = (relay.Node, )

class PetConnection(relay.Connection):
    class Meta:
        node = Pet

@api.schema("Pet")
class PetSchema(Schema):
    name = fields.Str()

pet_schema = PetSchema()
pets_schema = PetSchema(many=True)

@api.route("/pets/")
class PetsResource:
    def on_get(self, request, response):
        tmp_pets_all = PetModel.query.all()
        tmp_result = pets_schema.dump(tmp_pets_all).data
        response.media = tmp_result

@api.route("/pets/{id}/")
class PetResourceByID:
    def on_get(self, request, response, *, id):
        tmp_pet = PetModel.query.get(id)
        print("tmp_pet: {}".format(tmp_pet))
        if tmp_pet is None:
            response.status_code = api.status_codes.HTTP_400
            response.media = {'message': 'Pet could not be found.'}
            return
        tmp_result = pet_schema.dump(tmp_pet)
        response.media = tmp_result

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_pets = SQLAlchemyConnectionField(PetConnection)

schema = graphene.Schema(query=Query)
view = responder.ext.GraphQLView(api=api, schema=schema)

api.add_route("/graph", view)

if __name__ == '__main__':
    api.run()
