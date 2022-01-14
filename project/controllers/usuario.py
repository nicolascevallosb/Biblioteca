from flask                  import Blueprint, render_template, request, jsonify
from flask_login            import login_required, current_user
from sqlalchemy             import and_
from ..models.books         import Book
from ..models.borrowed      import Borrowed 
from project                import db 
import time, sqlite3, datetime

usuario = Blueprint('usuario', __name__)

######################################################## SEPARAR ADMIN Y ESTUDIANTE ########################################################

@usuario.route('/profile')
@login_required
def profile():
    
    c = sqlite3.connect('project/db.sqlite')
    cur = c.cursor()
    cur.execute("SELECT * from User")
    table_user = cur.fetchall()
    cur.execute("SELECT * from Book")
    table_book = cur.fetchall()
    cur.execute("SELECT * from Book WHERE stock > 0")
    table_available = cur.fetchall()
    cur.execute("SELECT * from Borrowed")
    table_borrowed = cur.fetchall()
    
    if(current_user.user_type == "Admin"): return render_template('admin/admin.html', table_user = table_user, table_book=table_book, user_name=current_user.name)
    if(current_user.user_type == "Student"): return render_template('student/student.html', table_user = table_user, table_book=table_available, table_borrowed=table_borrowed, user_name=current_user.name, id_student=current_user.id)

######################################################## BACK ADMIN ########################################################

######################################### AÑADIR LIBRO NUEVO #########################################

@usuario.route('/add')
@login_required
def add():
    return render_template('admin/admin-add.html')

@usuario.route('/ajax_add', methods=['POST'])
def ajax_add_post():
    
    _json = request.json
    responseMessage = {'message' : 'Libro(s) añadido(s) a la biblioteca exitosamente.'}
    responseStatusCode = 200

    time.sleep(1)
	
    code   = _json['code']
    title  = _json['title']
    author = _json['author']
    stock  = int(_json['stock'])
    book   = Book.query.filter_by(code=code).first()

    if book: 
        responseMessage = {'message' : 'Código ya existente, ingrese uno nuevo.'}
        responseStatusCode = 400
    
    else:

        book = Book(code=code, title=title, author=author, stock=stock)
        db.session.add(book)
        db.session.commit()
    
    response = jsonify(responseMessage)
    response.status_code = responseStatusCode

    return response

######################################### AÑADIR LIBRO EXISTENTE #########################################

@usuario.route('/add_existing', methods=['POST'])
@login_required
def add_existing():

    code        = request.form.get('code')
    book        = Book.query.filter_by(code=code).first()
    
    return render_template('admin/admin-add-existing.html', code=code, title=book.title, author=book.author, stock=book.stock)

@usuario.route('/ajax_add_existing', methods=['POST'])
def ajax_add_existing_post():
    
    _json = request.json
    print(_json)
    responseMessage = {'message' : 'Libro(s) añadido(s) exitosamente.'}
    responseStatusCode = 200

    time.sleep(1)

    code        = _json['code']
    new         = int(_json['new'])
    book        = Book.query.filter_by(code=code).first()
    
    book = Book.query.filter_by(code=code).first()
    db.session.delete(book)
    db.session.commit()
    
    book_update = Book(code=code, title=book.title, author=book.author, stock=book.stock + new)
    db.session.add(book_update)
    db.session.commit()
    
    response = jsonify(responseMessage)
    response.status_code = responseStatusCode

    return response

######################################### BUSCAR LIBRO POR SU CÓDIGO #########################################

@usuario.route('/ajax_search', methods=['POST'])
def ajax_search_post():
    
    _json = request.json
    code = _json['code']
    book = Book.query.filter_by(code=code).first()
    
    time.sleep(1)

    if book: 
        
        responseMessage = {'message' : f'Código: {book.code}\nTítulo: {book.title}\nAutor: {book.author}\nCantidad Disponible: {book.stock}'}
        responseStatusCode = 200
    
    else:

        responseMessage = {'message': f'Código {code} no encontrado.'}
        responseStatusCode = 400
    
    response = jsonify(responseMessage)
    response.status_code = responseStatusCode

    return response

######################################################## BACK ESTUDIANTE ########################################################

######################################### PRESTAR LIBRO #########################################

@usuario.route('/loan', methods=['POST'])
@login_required
def loan():

    code        = request.form.get('code')
    book        = Book.query.filter_by(code=code).first()
    issue_date  = datetime.datetime.now()
    
    return render_template('student/student-loan.html', code=code, title=book.title, author=book.author, issue_date=issue_date.strftime("%d/%m/%Y"), return_date=(issue_date + datetime.timedelta(days=30)).strftime("%d/%m/%Y"))

@usuario.route('/ajax_loan', methods=['POST'])
def ajax_loan_post():
    
    _json = request.json
    responseMessage = {'message' : 'Libro reservado exitosamente.'}
    responseStatusCode = 200

    time.sleep(1)
	
    id_student  = current_user.id
    code        = _json['code']
    title       = _json['title']
    author      = _json['author']
    issue_date  = _json['issue_date']
    return_date = _json['return_date']
    loan = False

    loans = Borrowed.query.filter_by(id_student=id_student).all()
    
    for current_loan in loans:
        if current_loan.code_borrowed == code:
            
            loan = True
            break
        
        else: loan = False
    
    if loan: 
        
        responseMessage = {'message': 'Libro ya reservado'}
        responseStatusCode = 400
    
    else:

        approved_loan = Borrowed(id_student=id_student, code_borrowed=code, title_borrowed=title, author_borrowed=author, issue_date=issue_date, return_date=return_date)
        db.session.add(approved_loan)
        db.session.commit()
        
        book = Book.query.filter_by(code=code).first()
        db.session.delete(book)
        db.session.commit()
        
        book_update = Book(code=code, title=book.title, author=book.author, stock=book.stock - 1)
        db.session.add(book_update)
        db.session.commit()
    
    response = jsonify(responseMessage)
    response.status_code = responseStatusCode

    return response
