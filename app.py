#----------------------------------------Imports-----------------------------------------------------

from flask import render_template, redirect, request, url_for, flash, make_response
from flask_login import current_user, login_required, logout_user, login_user 
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash

from Project import app, db, login_manager, forms
from Project.models import Favorieten, Opleidingsniveau, Overzicht, Studenten, Begeleiding, Stages

#----------------------------------------User Loader-------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return Studenten.query.get(user_id)

#----------------------------------------General routes-----------------------------------------------

@app.route("/")
def home():
    """
    Homepagina van de website
    """ 
    stages1 = Stages.query.filter(Stages.sector == 'ICT').limit(4).all()
    stages2 = Stages.query.filter(Stages.sector == 'Marketing').limit(4).all()

    return render_template("index.html", stages1=stages1, stages2=stages2)

@app.route("/stages", methods=['GET', 'POST'])
def stages():
    """
    Stages pagina van de website met een overzicht van alle stages
    """

    #--------------------Show Stages---------------------
    stages = Stages.query.all()

    #----------------------Forms-------------------------
    form = forms.LikeForm()

    #--------------Like Stage Unauthenticated-----------

    if request.method == 'POST':
        stage_id = request.form.get('stage_id')

        if stage_id:
            stage_id = int(stage_id)

            favorites_cookie = request.cookies.get('favorites')

            favorites = favorites_cookie.split(',') if favorites_cookie else []

            if str(stage_id) not in favorites:
                favorites.append(str(stage_id))

            favorites_cookie_value = ','.join(favorites)

            resp = make_response(render_template("stages.html", stages=stages, form=form))
            resp.set_cookie('favorites', favorites_cookie_value)
            flash('Stage toegevoegd aan favorieten', 'success')

            return resp

    #--------------Like Stage Authenticated--------------

    if current_user.is_authenticated and request.method == 'POST':
        stage_ids = request.form.getlist('stage_id')

        for stage_id in stage_ids:
            if stage_id:
                stage_id = int(stage_id)

        student_id = current_user.id

        existing_like = Favorieten.query.filter_by(student_id=student_id, stage_id=stage_id).first()

        if existing_like:
            flash('You have already liked this stage.', 'info')

        else:
            new_like = Favorieten(student_id=student_id, stage_id=stage_id)
            db.session.add(new_like)
            db.session.commit()
            flash('Stage succesvol gefavoriet!', 'success')

    return render_template("stages.html", stages=stages, form=form)


@app.route("/favorieten", methods=['GET', 'POST'])
def favorieten():
    """
    Display favorite stages for the current user
    """

    #-----------Show Favorite Stages-----------
    favorites_cookie = request.cookies.get('favorites')
    favorites = favorites_cookie.split(',') if favorites_cookie else []

    favorite_stages = Stages.query.filter(Stages.id.in_(favorites)).all()

    #-----------Unlike Favorite Stages-----------
    if request.method == 'POST':
        stage_id = request.form.get('stage_id')

        if stage_id and stage_id in favorites:
            favorites.remove(stage_id)
            favorites_cookie_value = ','.join(favorites)

            resp = make_response(redirect(url_for('favorieten')))
            resp.set_cookie('favorites', favorites_cookie_value)
            flash('Stage verwijdert uit favorieten', 'success')
            return resp

    return render_template("favorieten.html", favorite_stages=favorite_stages)


@app.route("/informatie")
def informatie():
    """
    Informatie pagina van de website met informatie over de website
    """

    return render_template("informatie.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login pagina van de website met een formulier om in te loggen
    """

    form = forms.LoginForm()
    if form.validate_on_submit():

        userStudent = Studenten.query.filter_by(email=form.email.data).first()
        userAdmin = Studenten.query.filter_by(id=1).first()

        if userAdmin and userAdmin.check_wachtwoord(form.wachtwoord.data):

            login_user(userAdmin)
            flash('Logged in succesvol!')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next_url = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('admin_stages')

            return redirect(next_url)

        elif userStudent and userStudent.check_wachtwoord(form.wachtwoord.data):

            # Log in the user
            login_user(userStudent)
            flash('Logged in succesvol!')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next_url = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('student_stage')

            return redirect(next_url)

    return render_template('login.html', form=form)


@app.route("/registreren", methods=['GET', 'POST'])
def registreren():
    """
    Registratie pagina van de website met een formulier om te registreren
    """

    form = forms.RegistratieForm()

    if form.validate_on_submit():
        student = Studenten(voornaam=form.voornaam.data,
                            achternaam=form.achternaam.data,
                            email=form.email.data,
                            wachtwoord=form.wachtwoord.data,
                            geboortedatum=form.geboortedatum.data,
                            straat=form.straat.data,
                            stad=form.stad.data,
                            provincie=form.provincie.data,
                            postcode=form.postcode.data,
                            opleidingsniveau_id=form.opleidingsniveau_id.data)

        db.session.add(student)
        db.session.commit()

        flash(u'Dank voor de registratie, Er kan nu ingelogd worden! ', 'success')

        return redirect(url_for('login'))

    return render_template('registreren.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """
    Logout pagina van de website
    """
    logout_user()
    flash('Je bent nu uitgelogd!')
    return redirect(url_for('home'))


#----------------------------------------Student routes-----------------------------------------------

@app.route("/student/overzicht", methods=['GET', 'POST'])
@login_required
def student_overzicht():
    """
    Overzicht pagina van de website voor studenten
    """

    #--------------------Show Overzicht---------------------
    overzicht = Overzicht.query.join(Studenten).filter_by(id=current_user.id).all()

    #------------------------Forms--------------------------
    form = forms.OverzichtStudentenWijzigenForm()

    if form.validate_on_submit():

        overzicht = Overzicht.query.filter_by(id_student=current_user.id).first()

        if overzicht is not None:
            if form.id_stage.data:
                overzicht.id_stage = form.id_stage.data
            if form.id_begeleider.data:
                overzicht.id_begeleider = form.id_begeleider.data
            if form.periode.data:
                overzicht.periode = form.periode.data

            db.session.commit()

            return redirect(url_for('student_overzicht'))

    return render_template("student-overzicht.html", overzicht=overzicht, form=form)


@app.route("/student/account", methods=['GET', 'POST'])
@login_required
def student_account():
    """
    Account pagina van de website voor studenten
    """

    student_id = current_user.id

    student = Studenten.query.filter_by(id=student_id).first()

    #--------------------Update Account---------------------
    form = forms.StudentenWijzigenForm()

    if form.is_submitted():
        if form.voornaam.data:
            student.voornaam = form.voornaam.data
        if form.achternaam.data:
            student.achternaam = form.achternaam.data
        if form.email.data:
            student.email = form.email.data
        if form.wachtwoord.data:
            student.wachtwoord = generate_password_hash(form.wachtwoord.data)
        if form.geboortedatum.data:
            student.geboortedatum = form.geboortedatum.data
        if form.straat.data:
            student.straat = form.straat.data
        if form.stad.data:
            student.stad = form.stad.data
        if form.provincie.data:
            student.provincie = form.provincie.data
        if form.postcode.data:
            student.postcode = form.postcode.data
        if form.opleidingsniveau_id.data:
            student.opleidingsniveau_id = form.opleidingsniveau_id.data

        db.session.commit()
        flash('Account succesvol gewijzigd!', 'success')
        return redirect(url_for('student_account'))

    return render_template("student-account.html", student=student, form=form)


@app.route("/student/stage", methods=['GET', 'POST'])
@login_required
def student_stage():
    """
    Stage pagina van de website voor studenten
    """

    #--------------------Show Stages---------------------
    favorieten = Favorieten.query.filter_by(student_id=current_user.id).options(
        joinedload(Favorieten.stages)).all()

    #----------------------Forms-------------------------
    form = forms.UnlikeForm()
    add_form = forms.StudentAanmeldenStageForm()

    #--------------------Aanmelden-----------------------

    if add_form.validate_on_submit():

        stage_ids = request.form.getlist('stage_id')

        for stage_id in stage_ids:
            if stage_id:
                stage_id = int(stage_id)

        student_id = current_user.id

        if Overzicht.query.filter_by(id_student=student_id).first():
            flash('Je bent al aangemeld bij een stage', 'error')
            return redirect(url_for('student_stage'))

        begeleider_id = add_form.begeleider_id.data
        periode = add_form.periode.data

        add = Overzicht(id_student=student_id, id_stage=stage_id, id_begeleider=begeleider_id, periode=periode)

        db.session.add(add)
        db.session.commit()

        flash('Stage succesvol toegevoegd!', 'success')

        return redirect(url_for('student_stage'))

    #---------------Unlike Authenticated----------------

    if form.is_submitted():

        stage_ids = request.form.getlist('stage_id')

        for stage_id in stage_ids:
            if stage_id:
                stage_id = int(stage_id)

        student_id = current_user.id

        like = Favorieten.query.filter_by(student_id=student_id, stage_id=stage_id).first()

        db.session.delete(like)
        db.session.commit()

        return redirect(url_for('student_stage'))

    return render_template("student-stage.html", favorieten=favorieten, form=form, add_form=add_form)


#----------------------------------------Admin routes----------------------------------------------------

@app.route("/admin/begeleiders", methods=['GET', 'POST'])
@login_required
def admin_begeleiders():
    """
    Begeleiders pagina van de website voor administrators
    """

    #--------------------Show Begeleiders---------------------

    begeleider = Begeleiding.query.all()

    #-------------------Update, Add, Delete Begeleider---------------------
    update_form = forms.BegeleiderWijzigenForm()
    delete_form = forms.BegeleiderVerwijderenForm()
    form = forms.BegeleiderToevoegenForm()

    # Process form submissions
    if form.validate_on_submit():
        begeleider = Begeleiding(voornaam=form.voornaam.data,
                                 achternaam=form.achternaam.data,
                                 afdeling=form.afdeling.data)

        db.session.add(begeleider)
        db.session.commit()

        return redirect(url_for('admin_begeleiders'))

    elif update_form.validate_on_submit():
        id = update_form.id.data
        begeleider = Begeleiding.query.filter_by(id=id).first()

        if update_form.voornaam.data:
            begeleider.voornaam = update_form.voornaam.data
        if update_form.achternaam.data:
            begeleider.achternaam = update_form.achternaam.data
        if update_form.afdeling.data:
            begeleider.afdeling = update_form.afdeling.data

        db.session.commit()

        return redirect(url_for('admin_begeleiders'))

    elif delete_form.validate_on_submit():
        id = delete_form.id.data
        begeleider = Begeleiding.query.filter_by(id=id).first()

        db.session.delete(begeleider)
        db.session.commit()

        return redirect(url_for('admin_begeleiders'))

    return render_template("admin-begeleiders.html", begeleider=begeleider, form=form, delete_form=delete_form,
                           update_form=update_form)


@app.route("/admin/stages", methods=['GET', 'POST'])
@login_required
def admin_stages():
    """
    Begeleiders pagina van de website voor administrators
    """

    # --------------------Show Stages---------------------

    stages = Stages.query.join(Opleidingsniveau).all()

    # --------------------Add, Delete, Update Stage---------------------

    delete_form = forms.StageVerwijderenForm()
    form = forms.StageToevoegenForm()
    update_form = forms.StageWijzigenForm()

    if form.validate_on_submit():
        stage = Stages(bedrijfsnaam=form.bedrijfsnaam.data,
                       sector=form.sector.data,
                       beschrijving=form.beschrijving.data,
                       image_link=form.image_link.data,
                       stad=form.stad.data,
                       stage_duur=form.stage_duur.data,
                       functie=form.functie.data,
                       opleidingsniveau_id=form.opleidingsniveau_id.data)

        db.session.add(stage)
        db.session.commit()

        return redirect(url_for('admin_stages'))


    elif delete_form.validate_on_submit():

        bedrijfsnaam = delete_form.bedrijfsnaam.data
        stage = Stages.query.filter_by(bedrijfsnaam=bedrijfsnaam).first()

        if stage:
            db.session.delete(stage)
            db.session.commit()

            return redirect(url_for('admin_stages'))

    elif update_form.validate_on_submit():
        stage_id = update_form.id.data
        stage = Stages.query.get(stage_id)

        if stage:
            if update_form.bedrijfsnaam.data:
                stage.bedrijfsnaam = update_form.bedrijfsnaam.data
            if update_form.sector.data:
                stage.sector = update_form.sector.data
            if update_form.beschrijving.data:
                stage.beschrijving = update_form.beschrijving.data
            if update_form.image_link.data:
                stage.image_link = update_form.image_link.data
            if update_form.stad.data:
                stage.stad = update_form.stad.data
            if update_form.stage_duur.data:
                stage.stage_duur = update_form.stage_duur.data
            if update_form.functie.data:
                stage.functie = update_form.functie.data
            if update_form.opleidingsniveau_id.data:
                stage.opleidingsniveau_id = update_form.opleidingsniveau_id.data

            db.session.commit()

            return redirect(url_for('admin_stages'))

    return render_template("admin-stages.html", stages=stages, form=form, delete_form=delete_form,
                           update_form=update_form)


@app.route("/admin/studenten", methods=['GET', 'POST'])
@login_required
def admin_studenten():
    """
    Begeleiders pagina van de website voor administrators
    """

    #--------------------Show Studenten---------------------
    students = Studenten.query.all()

    #-------------Update, Add, Delete Student---------------
    update_form = forms.StudentenWijzigenForm()
    delete_form = forms.StudentenVerwijderenForm()
    form = forms.RegistratieForm()

    if form.validate_on_submit():

        student = Studenten(voornaam=form.voornaam.data,
                            achternaam=form.achternaam.data,
                            email=form.email.data,
                            wachtwoord=form.wachtwoord.data,
                            geboortedatum=form.geboortedatum.data,
                            straat=form.straat.data,
                            stad=form.stad.data,
                            provincie=form.provincie.data,
                            postcode=form.postcode.data,
                            opleidingsniveau_id=form.opleidingsniveau_id.data)

        db.session.add(student)
        db.session.commit()

        return redirect(url_for('admin_studenten'))

    elif update_form.is_submitted() and update_form.id.data:
        student_id = update_form.id.data
        student = Studenten.query.get(student_id)

        if update_form.voornaam.data:
            student.voornaam = update_form.voornaam.data
        if update_form.achternaam.data:
            student.achternaam = update_form.achternaam.data
        if update_form.email.data:
            student.email = update_form.email.data
        if update_form.wachtwoord.data:
            student.wachtwoord = update_form.wachtwoord.data
        if update_form.geboortedatum.data:
            student.geboortedatum = update_form.geboortedatum.data
        if update_form.straat.data:
            student.straat = update_form.straat.data
        if update_form.stad.data:
            student.stad = update_form.stad.data
        if update_form.provincie.data:
            student.provincie = update_form.provincie.data
        if update_form.postcode.data:
            student.postcode = update_form.postcode.data
        if update_form.opleidingsniveau_id.data:
            student.opleidingsniveau_id = update_form.opleidingsniveau_id.data

            db.session.commit()

        return redirect(url_for('admin_studenten'))


    elif delete_form.validate_on_submit():
        id = delete_form.id.data

        student = Studenten.query.filter_by(id=id).first()

        if student:
            db.session.delete(student)
            db.session.commit()

        return redirect(url_for('admin_studenten'))

    return render_template("admin-studenten.html", form=form, delete_form=delete_form, update_form=update_form,
                           students=students)


@app.route("/admin/overzicht", methods=['GET', 'POST'])
@login_required
def admin_overzicht():
    """
    Overzicht pagina van de website voor administrators
    """

    #--------------------Show Studenten---------------------

    overzicht = Overzicht.query.join(Studenten).join(Stages).join(Begeleiding).all()

    #--------------Update, Add, Delete Student--------------
    add_student = forms.StudentStageAanmelden()
    add_cijfer = forms.CijferToevoegenForm()
    update_form = forms.OverzichtWijzigenForm()
    delete_form = forms.OverzichtVerwijderenForm()

    if add_student.validate_on_submit():

        student_id = add_student.student_id.data
        stage_id = add_student.stage_id.data
        begeleider_id = add_student.begeleider_id.data
        periode = add_student.periode.data

        existing_overzicht = Overzicht.query.filter_by(id_student=student_id).first()

        if existing_overzicht is None:
            overzicht = Overzicht(id_student=student_id, id_stage=stage_id, id_begeleider=begeleider_id,
                                  periode=periode)
            db.session.add(overzicht)
            db.session.commit()
        else:
            flash('Deze student is al aangemeld bij een stage', 'error')

        return redirect(url_for('admin_overzicht'))

    elif add_cijfer.validate_on_submit():

        if add_cijfer.cijfer.data < 1 or add_cijfer.cijfer.data > 10:
            flash('Cijfer moet tussen de 1 en 10 liggen', 'error')
            return redirect(url_for('admin_overzicht'))

        else:
            cijfer = add_cijfer.cijfer.data
            overzicht_id = add_cijfer.overzicht_id.data

            overzicht = Overzicht.query.filter_by(id=overzicht_id).first()
            overzicht.cijfer = cijfer

            db.session.commit()

            return redirect(url_for('admin_overzicht'))

    elif update_form.validate_on_submit():

        overzicht_id = int(update_form.overzicht_id.data)
        overzicht = Overzicht.query.filter_by(id=overzicht_id).first()

        if update_form.id_stage.data:
            overzicht.id_stage = update_form.id_stage.data
        if update_form.id_begeleider.data:
            overzicht.id_begeleider = update_form.id_begeleider.data
        if update_form.periode.data:
            overzicht.periode = update_form.periode.data

        db.session.commit()

        return redirect(url_for('admin_overzicht'))

    elif delete_form.validate_on_submit():

        overzicht_id = delete_form.overzicht_id.data
        overzicht = Overzicht.query.filter_by(id=overzicht_id).first()

        db.session.delete(overzicht)
        db.session.commit()

        return redirect(url_for('admin_overzicht'))

    return render_template("admin-overzicht.html", overzicht=overzicht, add_student=add_student, add_cijfer=add_cijfer,
                           update_form=update_form, delete_form=delete_form)


#--------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
