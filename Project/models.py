#-----------------------------Imports---------------------------------
from sqlalchemy import Column, Float, ForeignKey, Integer, Text, String
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

#-----------------------------Tables----------------------------------

class Opleidingsniveau(db.Model):
    __tablename__ = 'opleidingsniveau'
    
    """
    Table opleidingsniveau in database StageMetGert with the following columns:

    ID -- primary key
    niveau -- niveau
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    niveau = Column(Text, nullable=False)

    stages = relationship("Stages", back_populates="opleidingsniveau")
    studenten = relationship("Studenten", back_populates="opleidingsniveau")

    def __init__(self, niveau):
        self.niveau = niveau
        
#---------------------------------------------------------------------
        
class Stages(db.Model):
    __tablename__ = 'stages'
    """
    Table stages in database StageMetGert with the following columns:

    ID -- primary key
    naam -- name of the stage
    sector -- sector of the stage
    beschrijving -- description of the stage
    image_link -- link to image of the stage
    type -- relationship with types table
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    bedrijfsnaam = Column(String, nullable=False)
    sector = Column(String)
    beschrijving = Column(String)
    image_link = Column(String)
    stad = Column(String)
    stage_duur = Column(String)
    functie = Column(String)
    opleidingsniveau_id = Column(String, ForeignKey('opleidingsniveau.id'))

    favorieten = relationship("Favorieten", back_populates="stages")
    overzichten = relationship("Overzicht", back_populates="stages")
    opleidingsniveau = relationship("Opleidingsniveau", back_populates="stages")


    def __init__(self, bedrijfsnaam, sector, beschrijving, image_link, stad, stage_duur, functie, opleidingsniveau_id):
        self.bedrijfsnaam = bedrijfsnaam
        self.sector = sector
        self.beschrijving = beschrijving
        self.image_link = image_link
        self.stad = stad
        self.stage_duur = stage_duur
        self.functie = functie
        self.opleidingsniveau_id = opleidingsniveau_id
        
#---------------------------------------------------------------------

class Studenten(db.Model,UserMixin):
    __tablename__ = 'studenten'
    """
    Table studenten in database StageMetGert met de volgende kolommen:

    id -- primary key
    voornaam -- voornaam van de student
    achternaam -- achternaam van de student
    email -- email van de student

    overzichten -- relatie met tabel overzichten
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    voornaam = Column(Text, nullable=False)
    achternaam = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    wachtwoord = Column(Text, nullable=False, unique=True)
    geboortedatum = Column(String)
    straat = Column(String)
    stad = Column(String)
    provincie = Column(String)
    postcode = Column(String)
    opleidingsniveau_id = Column(String, ForeignKey('opleidingsniveau.id'))

    overzicht = relationship("Overzicht", back_populates="studenten")
    favorieten = relationship("Favorieten", back_populates="studenten")
    opleidingsniveau = relationship("Opleidingsniveau", back_populates="studenten")


    def __init__(self, voornaam, achternaam, email, wachtwoord, geboortedatum, straat, stad, provincie, postcode, opleidingsniveau_id):
        self.voornaam = voornaam
        self.achternaam = achternaam
        self.email = email
        self.wachtwoord = generate_password_hash(wachtwoord)
        self.geboortedatum = geboortedatum
        self.straat = straat
        self.stad = stad
        self.provincie = provincie
        self.postcode = postcode
        self.opleidingsniveau_id = opleidingsniveau_id

    def check_wachtwoord(self, wachtwoord):
        return check_password_hash(self.wachtwoord, wachtwoord)
    
#---------------------------------------------------------------------

class Begeleiding(db.Model,UserMixin):
    __tablename__ = 'begeleiding'

    """
    Table begeleiding in database StageMetGert met de volgende kolommen:

    id -- primary key
    voornaam -- voornaam van de begeleider
    achternaam -- achternaam van de begeleider
    email -- email van de begeleider
    wachtwoord -- wachtwoord van de begeleider
    
    overzichten -- relatie met tabel overzichten
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    voornaam = Column(Text, nullable=False)
    achternaam = Column(Text, nullable=False)
    afdeling = Column(String)

    overzichten = relationship("Overzicht", back_populates="begeleiding")

    def __init__(self, voornaam, achternaam, afdeling):
        self.voornaam = voornaam
        self.achternaam = achternaam
        self.afdeling = afdeling

#---------------------------------------------------------------------

class Overzicht(db.Model):
    __tablename__ = 'overzicht'
    """
    Table overzichten in database StageMetGert met de volgende kolommen:
    
    id -- primary key
    id_student -- foreign key naar tabel studenten
    id_instelling -- foreign key naar tabel instellingen
    id_begeleider -- foreign key naar tabel begeleiding
    cijfer -- cijfer van de student
    Periode -- periode van de stage

    studenten -- relatie met tabel studenten
    stages -- relatie met tabel stages
    begeleiding -- relatie met tabel begeleiding
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_student = Column(db.Integer, db.ForeignKey('studenten.id'))
    id_stage = Column(Integer, ForeignKey('stages.id'), nullable=False)
    id_begeleider = Column(Integer, ForeignKey('begeleiding.id'), nullable=False)
    cijfer = Column(Float)
    periode = Column(String)

    studenten = relationship('Studenten')
    stages = relationship("Stages", back_populates="overzichten")
    begeleiding = relationship("Begeleiding", back_populates="overzichten")

    def __init__(self, id_student, id_stage, id_begeleider, periode):
        self.id_student = id_student
        self.id_stage = id_stage
        self.id_begeleider = id_begeleider
        self.periode = periode

#---------------------------------------------------------------------
    
class Favorieten(db.Model):
    __tablename__ = 'favorieten'
    """ 
    Table favorieten in database StageMetGert with the following columns:
    
    ID -- primary key
    student_id -- foreign key to studenten table
    stage_id -- foreign key to stages table
    """

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    student_id = Column(Integer, ForeignKey('studenten.id'), nullable=False)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)

    studenten = relationship("Studenten", back_populates="favorieten")
    stages = relationship("Stages", back_populates="favorieten")
