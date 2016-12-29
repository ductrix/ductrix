from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData
import uuid

class dbaccess:

    def __init__(self, db_con_string, userschema):
        self.db_con_string = db_con_string
        self.schema = userschema
        self.engine = create_engine(self.db_con_string)

        #m = MetaData(schema='db1')
        self.m = MetaData(schema=self.schema)
        self.Base = automap_base(bind=self.engine, metadata=self.m)

        # reflect the tables
        self.Base.prepare(self.engine, reflect=True) 
    # mapped classes are now created with names by default
    # matching that of the table name.
    def get_session(self):
        self.session = Session(self.engine)
        return self.session 

    def get_pooltbl(self):
        Pooltable = self.Base.classes.pooltable
        return Pooltable

    def get_servertbl(self):
        Servertable = self.Base.classes.servertable
        return Servertable

    def get_dbtbl(self):
        Dbtable = self.Base.classes.dbtable
        return Dbtable

    def get_privatepooltbl(self):
        Privatepool = self.Base.classes.privatepool
        return Privatepool

    def get_publicpooltbl(self):
        Publicpool = self.Base.classes.publicpool
        return Publicpool

    def get_uuid(self):
        return str(uuid.uuid4())

