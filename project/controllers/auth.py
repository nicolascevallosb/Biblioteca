from flask              import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login        import login_user, logout_user, login_required
from werkzeug.security  import generate_password_hash, check_password_hash
from ..models.users     import User
from project            import db 
import time

auth = Blueprint('auth', __name__)

######################################################## BACK AUTENTICACIÓN ########################################################

######################################### SIGN UP #########################################

@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')

@auth.route('/ajax_signup', methods=['POST'])
def ajax_signup_post():
    _json = request.json
    responseMessage = {'message' : 'La cuenta fue creada con éxito.'}
    responseStatusCode = 200

    time.sleep(1)
	
    email    = _json['email']
    name     = _json['name']
    user_type = _json['user_type']
    password = _json['password']

    user = User.query.filter_by(email=email).first()

    if user: 
    
        responseMessage = {'message' : 'Correo electrónico ya utilizado.'}
        responseStatusCode = 400
    
    else:

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), user_type=user_type)

        db.session.add(new_user)
        db.session.commit()
    
    response = jsonify(responseMessage)
    response.status_code = responseStatusCode

    return response

######################################### LOG IN #########################################

@auth.route('/login')
def login():
    return render_template('auth/login.html')

@auth.route('/ajax_login', methods=['POST'])
def ajax_login():
    
    _json = request.json
    responseMessage = {'message' : 'Log in successful'}
    responseStatusCode = 200
    remember = True if request.form.get('remember') else False
    
    time.sleep(1)

    email = _json['email']
    password = _json['password']
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        
        responseMessage = {'message':'Please check your login details and try again.'}
        responseStatusCode = 400 
    
    else: login_user(user, remember=remember)

    response = jsonify(responseMessage)
    response.status_code = responseStatusCode

    return(response) 

######################################### LOG OUT #########################################

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
