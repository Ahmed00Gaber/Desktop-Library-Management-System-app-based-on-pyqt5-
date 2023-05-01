from peewee import *

#create data base
db = MySQLDatabase('myapp', user='root', password='ahmedgaber011',
                         host='localhost', port=3306)

class Person(Model):
    #col in table
    name = CharField() #char type
    birthday = DateField() #int

    class Meta:
        database = db # This model uses the "people.db" database.\
class Pet(Model):
    # relation between person and pet 1 to many  fK was on the many side
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()
    class Meta:
        database = db       

db.connect()
#don't forget to update create table after you finish to appers
db.create_tables([Person, Pet])