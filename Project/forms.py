#----------------------------------Imports-----------------------------------------------------
from flask_wtf import FlaskForm
from wtforms import (HiddenField, StringField, SelectField, SubmitField, PasswordField, EmailField)
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from .models import Studenten, Begeleiding, Stages, Overzicht

#----------------------------------Favorieten Form---------------------------------------------

class LikeForm(FlaskForm):
    """
    Formulier voor het toevoegen van een stage aan favorieten met de volgende velden:

    post_id -- ID van de stage
    """

    stage_id = HiddenField('Post ID', validators=[DataRequired()])
    submit = SubmitField('❤️')

class UnlikeForm(FlaskForm):
    """
    Formulier voor het verwijderen van een stage van favorieten met de volgende velden:

    post_id -- ID van de stage
    """

    stage_id = HiddenField('Post ID', validators=[DataRequired()])
    submit = SubmitField('❌')

#----------------------------------Login Form--------------------------------------------------

class LoginForm(FlaskForm):
    """
    Formulier voor het inloggen van een student met de volgende velden:

    email -- email van de student
    wachtwoord -- wachtwoord van de student
    submit -- knop om het formulier te versturen

    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    wachtwoord = PasswordField('Wachtwoord', validators=[DataRequired()])
    submit = SubmitField('Inloggen')

#----------------------------------Studenten Forms---------------------------------------------

class RegistratieForm(FlaskForm):

    """
    Formulier voor het registreren van een student met de volgende velden:

    voornaam -- voornaam van de student
    achternaam -- achternaam van de student
    email -- email van de student
    wachtwoord -- wachtwoord van de student
    wachtwoord_comf -- bevestiging van het wachtwoord van de student
    geboortedatum -- geboortedatum van de student
    straat -- straat van de student
    stad -- stad van de student
    provincie -- provincie van de student
    postcode -- postcode van de student
    opleidingsniveau -- opleidingsniveau van de student
    submit -- knop om het formulier te versturen
    """

    voornaam = StringField('Voornaam', validators=[DataRequired()])
    achternaam = StringField('Achternaam', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    wachtwoord = PasswordField('Wachtwoord', validators=[DataRequired(), EqualTo('wachtwoord_comf', message='Wachtwoorden moeten gelijk zijn!'), Length(min=8)])
    wachtwoord_comf = PasswordField('Bevestig uw wachtwoord', validators=[DataRequired(),Length(min=8)])
    geboortedatum = StringField('Geboortedatum', validators=[DataRequired()])
    straat = StringField('Straat', validators=[DataRequired()])
    stad = StringField('Stad', validators=[DataRequired()])
    provincie = StringField('Provincie', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    opleidingsniveau_id = SelectField('Opleidingsniveau', choices=[('1', 'HBO'), ('2', 'WO'), ('3', 'MBO')], validators=[DataRequired()])
    submit = SubmitField('Registeren')

    def validate_email(self, field):
        if Studenten.query.filter_by(email=field.data).first():
            raise ValidationError('Dit e-mailadres staat al geregistreerd!')

class StudentenVerwijderenForm(FlaskForm):
    """
    Formulier voor het verwijderen van studenten
    """

    id = SelectField('Student', validators=[DataRequired()])
    submit = SubmitField('Verwijderen')

    def __init__(self, *args, **kwargs):
        super(StudentenVerwijderenForm, self).__init__(*args, **kwargs)
        self.id.choices = [(student.id, f"{student.voornaam} {student.achternaam}") for student in Studenten.query.filter(Studenten.id > 1).all()]

class StudentenWijzigenForm(FlaskForm):
    """
    Formulier voor het wijzigen van studenten
    """

    id = SelectField('Welke student', validators=[DataRequired()])
    voornaam = StringField('Voornaam')
    achternaam = StringField('Achternaam')
    email = StringField('Email', validators=[Email()])
    wachtwoord = PasswordField('Wachtwoord', validators=[EqualTo('wachtwoord_comf', message='Wachtwoorden moeten gelijk zijn!')])
    wachtwoord_comf = PasswordField('Bevestig uw wachtwoord')
    geboortedatum = StringField('Geboortedatum')
    straat = StringField('Straat')
    stad = StringField('Stad')
    provincie = StringField('Provincie')
    postcode = StringField('Postcode')
    opleidingsniveau_id = SelectField('Opleidingsniveau', choices=[('1', 'HBO'), ('2', 'WO'), ('3', 'MBO')])
    submit = SubmitField('Wijzigen', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(StudentenWijzigenForm, self).__init__(*args, **kwargs)
        self.id.choices = [(student.id, f"{student.voornaam} {student.achternaam}") for student in Studenten.query.filter(Studenten.id > 1).all()]

class OverzichtStudentenWijzigenForm(FlaskForm):
    """
    Formulier voor het wijzigen van een overzicht
    """

    id_stage = SelectField('Stage')
    id_begeleider = SelectField('Begeleider')
    periode = StringField('Periode')
    submit = SubmitField('Wijzigen')

    def __init__(self, *args, **kwargs):
        super(OverzichtStudentenWijzigenForm, self).__init__(*args, **kwargs)
        self.id_stage.choices = [('', 'Select Stage')] + [(str(stage.id), stage.bedrijfsnaam) for stage in Stages.query.all()]
        self.id_begeleider.choices = [('', 'Select Begeleider')] + [(str(begeleider.id), begeleider.voornaam + ' ' + begeleider.achternaam) for begeleider in Begeleiding.query.all()]

#----------------------------------Begeleiders Forms-------------------------------------------

class BegeleiderToevoegenForm(FlaskForm):
    """
    Formulier voor het toevoegen van een begeleider
    """

    voornaam = StringField('Voornaam', validators=[DataRequired()])
    achternaam = StringField('Achternaam', validators=[DataRequired()])
    afdeling = SelectField('Afdeling', choices=[('ICT', 'ICT'), ('Marketing', 'Marketing')])
    submit = SubmitField('Registeren')

class BegeleiderVerwijderenForm(FlaskForm):
    """
    Formulier voor het verwijderen van een begeleider
    """

    id = SelectField('Begeleider', validators=[DataRequired()])
    submit = SubmitField('Verwijderen')

    def __init__(self, *args, **kwargs):
        super(BegeleiderVerwijderenForm, self).__init__(*args, **kwargs)
        self.id.choices = [(begeleider.id, f"{begeleider.voornaam} {begeleider.achternaam}") for begeleider in Begeleiding.query.all()]

class BegeleiderWijzigenForm(FlaskForm):
    """
    Formulier voor het wijzigen van een begeleider
    """

    id = SelectField('Welke begeleider', validators=[DataRequired()])
    voornaam = StringField('Voornaam')
    achternaam = StringField('Achternaam')
    afdeling = SelectField('Afdeling', choices=[('ICT', 'ICT'), ('Marketing', 'Marketing')])
    submit = SubmitField('Wijzigen')

    def __init__(self, *args, **kwargs):
        super(BegeleiderWijzigenForm, self).__init__(*args, **kwargs)
        self.id.choices = [(begeleider.id, f"{begeleider.voornaam} {begeleider.achternaam}") for begeleider in Begeleiding.query.all()]

#----------------------------------------Stage Forms-------------------------------------------------

class StageToevoegenForm(FlaskForm):
    """
    Form for adding entries to the stages table with the following fields:

    bedrijfsnaam -- name of the company offering the stage
    sector -- sector of the stage (ICT or Marketing)
    beschrijving -- description of the stage
    image_link -- link to the image associated with the stage
    begeleider_id -- ID of the supervisor associated with the stage
    stad -- city where the stage is located
    stage_duur -- duration of the stage
    functie -- role of the stage
    opleidingsniveau_id -- ID of the education level required for the stage
    """

    bedrijfsnaam = StringField('Bedrijfsnaam', validators=[DataRequired()])
    sector = SelectField('Sector', choices=[('ICT', 'ICT'), ('Marketing', 'Marketing')], validators=[DataRequired()])
    beschrijving = StringField('Beschrijving', validators=[DataRequired()])
    image_link = StringField('Image Link')
    begeleider_id = SelectField('Begeleider', coerce=int)
    stad = StringField('Stad', validators=[DataRequired()])
    stage_duur = StringField('Stage Duur', validators=[DataRequired()])
    functie = StringField('Functie', validators=[DataRequired()])
    opleidingsniveau_id = SelectField('Opleidingsniveau', choices=[('1', 'HBO'), ('2', 'WO'), ('3', 'MBO')], validators=[DataRequired()])
    submit = SubmitField('Toevoegen')

    def __init__(self, *args, **kwargs):
        super(StageToevoegenForm, self).__init__(*args, **kwargs)
        self.begeleider_id.choices = [(begeleider.id, begeleider.voornaam) for begeleider in Begeleiding.query.all()]

class StageVerwijderenForm(FlaskForm):
    """
    Form for deleting entries from the stages table with the following fields:

    bedrijfsnaam -- name of the company offering the stage
    """

    bedrijfsnaam = SelectField('Bedrijfsnaam', validators=[DataRequired()])
    submit = SubmitField('Verwijderen')

    def __init__(self, *args, **kwargs):
        super(StageVerwijderenForm, self).__init__(*args, **kwargs)
        self.bedrijfsnaam.choices = [(stage.bedrijfsnaam) for stage in Stages.query.all()]

class StageWijzigenForm(FlaskForm):
    """
    Form for changing entries in the stages table with the following fields:

    bedrijfsnaam -- name of the company offering the stage
    sector -- sector of the stage (ICT or Marketing)
    beschrijving -- description of the stage
    image_link -- link to the image associated with the stage
    begeleider_id -- ID of the supervisor associated with the stage
    stad -- city where the stage is located
    stage_duur -- duration of the stage
    functie -- role of the stage
    opleidingsniveau_id -- ID of the education level required for the stage
    """

    id = SelectField('Waar wil je wijzigen', validators=[DataRequired()])
    bedrijfsnaam = StringField('Bedrijfsnaam')
    sector = SelectField('Sector', choices=[('ICT', 'ICT'), ('Marketing', 'Marketing')])
    beschrijving = StringField('Beschrijving')
    image_link = StringField('Image Link')
    begeleider_id = SelectField('Begeleider', coerce=int)
    stad = StringField('Stad')
    stage_duur = StringField('Stage Duur')
    functie = StringField('Functie')
    opleidingsniveau_id = SelectField('Opleidingsniveau', choices=[('1', 'HBO'), ('2', 'WO'), ('3', 'MBO')])
    submit = SubmitField('Wijzigen')

    def __init__(self, *args, **kwargs):
        super(StageWijzigenForm, self).__init__(*args, **kwargs)
        self.begeleider_id.choices = [(begeleider.id, begeleider.voornaam) for begeleider in Begeleiding.query.all()]
        self.id.choices = [(stage.id, f"{stage.id}: {stage.bedrijfsnaam}") for stage in Stages.query.all()]

#----------------------------------Stage Student Forms------------------------------------------------

class StudentAanmeldenStageForm(FlaskForm):
    """
    Formulier voor het aanmelden van een stage
    """
    stage_id = HiddenField('Post ID')
    begeleider_id = SelectField('Begeleider', coerce=int, validators=[DataRequired()])
    periode = StringField('Periode', validators=[DataRequired()])
    submit = SubmitField('Aanmelden')

    def __init__(self, *args, **kwargs):
        super(StudentAanmeldenStageForm, self).__init__(*args, **kwargs)
        self.begeleider_id.choices = [(begeleider.id, f'{begeleider.voornaam} {begeleider.achternaam}') for begeleider in Begeleiding.query.all()]

class StudentAfmeldenStageForm(FlaskForm):
    """
    Formulier voor het afmelden van een stage
    """

    stage_id = HiddenField('Post ID', validators=[DataRequired()])
    submit = SubmitField('➖')

#----------------------------------Stage Admin Forms-------------------------------------------------

class StudentStageAanmelden(FlaskForm):
    """
    Formulier voor het aanmelden van een student voor een stage
    """

    student_id = SelectField('Student', validators=[DataRequired()])
    stage_id = SelectField('Stage')
    begeleider_id = SelectField('Begeleider')
    periode = StringField('Periode', validators=[DataRequired()])
    submit = SubmitField('Aanmelden')

    def __init__(self, *args, **kwargs):
        super(StudentStageAanmelden, self).__init__(*args, **kwargs)
        self.student_id.choices = [('', 'Select Student')] + [(str(student.id), student.voornaam + ' ' + student.achternaam) for student in Studenten.query.filter(Studenten.id > 1).all()]
        self.stage_id.choices = [('', 'Select Stage')] + [(str(stage.id), stage.bedrijfsnaam) for stage in Stages.query.all()]
        self.begeleider_id.choices = [('', 'Select Begeleider')] + [(str(begeleider.id), begeleider.voornaam + ' ' + begeleider.achternaam) for begeleider in Begeleiding.query.all()]

class CijferToevoegenForm(FlaskForm):
    """
    Formulier voor het toevoegen van cijfers aan een stage met de volgende velden:

    student_name -- naam van de student
    cijfer -- cijfer van de stage
    submit -- knop om het formulier te versturen

    """
    overzicht_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    cijfer = FloatField('Cijfer', validators=[DataRequired()])
    submit = SubmitField('Toevoegen')

    def __init__(self, *args, **kwargs):
        super(CijferToevoegenForm, self).__init__(*args, **kwargs)
        self.overzicht_id.choices = [(overzicht.id, overzicht.studenten.voornaam + ' ' + overzicht.studenten.achternaam) for overzicht in Overzicht.query.join(Studenten).all()]

class OverzichtWijzigenForm(FlaskForm):
    """
    Formulier voor het wijzigen van een overzicht
    """

    overzicht_id = SelectField('Student', validators=[DataRequired()])
    id_stage = SelectField('Stage')
    id_begeleider = SelectField('Begeleider')
    periode = StringField('Periode')
    submit = SubmitField('Wijzigen')

    def __init__(self, *args, **kwargs):
        super(OverzichtWijzigenForm, self).__init__(*args, **kwargs)
        self.id_stage.choices = [('', 'Select Stage')] + [(str(stage.id), stage.bedrijfsnaam) for stage in Stages.query.all()]
        self.id_begeleider.choices = [('', 'Select Begeleider')] + [(str(begeleider.id), begeleider.voornaam + ' ' + begeleider.achternaam) for begeleider in Begeleiding.query.all()]
        self.overzicht_id.choices = [('', 'Select Student')] + [(str(overzicht.id), overzicht.studenten.voornaam + ' ' + overzicht.studenten.achternaam) for overzicht in Overzicht.query.join(Studenten).all()]

class OverzichtVerwijderenForm(FlaskForm):
    """
    Formulier voor het verwijderen van een overzicht
    """

    overzicht_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Verwijderen')

    def __init__(self, *args, **kwargs):
        super(OverzichtVerwijderenForm, self).__init__(*args, **kwargs)
        self.overzicht_id.choices = [(overzicht.id, overzicht.studenten.voornaam + ' ' + overzicht.studenten.achternaam) for overzicht in Overzicht.query.join(Studenten).all()]