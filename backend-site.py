
from datetime import datetime, timedelta
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Library.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

# <------------Step 1 create DB---------->
class Books(db.Model):
    BookId = db.Column('BookId',db.Integer, primary_key=True)
    NameBook = db.Column('NameBook',db.String(50))
    Author = db.Column('Author',db.String(50), nullable=False )
    YearPublished = db.Column('YearPublished',db.String(50))
    Type = db.Column('Type',db.Integer)
    BooksToLoans = db.relationship('Loans', backref='books')

    def __init__(self, NameBook, Author, YearPublished, Type):
        self.NameBook = NameBook.title()
        self.Author = Author.title()
        self.YearPublished = YearPublished
        self.Type = Type

class Customers(db.Model):
    CusomerID = db.Column('CusomerID',db.Integer, primary_key=True)
    Name = db.Column('Name', db.String(50))
    City = db.Column('City', db.String(50))
    Age = db.Column('Age', db.Integer)
    CustomersToLoans = db.relationship('Loans', backref='customers')
                       
    def __init__(self, CusomerID, Name, City, Age):
        self.CusomerID = CusomerID
        self.Name = Name.title()
        self.City = City
        self.Age = Age

class Loans(db.Model):
    LoansID = db.Column('LoansID', db.Integer, primary_key=True)
    CusomerID = db.Column('CusomerID', db.Integer, db.ForeignKey('customers.CusomerID'), nullable=False)
    BookId = db.Column('BookId', db.Integer, db.ForeignKey('books.BookId'))
    LoanDate = db.Column('LoanDate', db.Date)
    ReturnDate = db.Column('ReturnDate', db.Date)
    
    def __init__(self, CusomerID, BookId, LoanDate, ReturnDate):
        self.CusomerID = CusomerID
        self.BookId = BookId
        self.LoanDate = LoanDate
        self.ReturnDate = ReturnDate

# <------------Step 2 bild all function---------->
@app.route('/')
def HomePage():
    """H"""
    return render_template('index.html')


@app.route('/addCustomer/', methods=['POST', 'GET'])
def AddCustomer():
    id_reserved = Customers.query.all()
    for id in id_reserved:
        if request.method == 'POST':
            if 1 <=  int(request.form['ID']) != id.CusomerID:
                NewCustomer = Customers(CusomerID=request.form['ID'], Name=request.form['Name'],
                                        City=request.form['City'], Age=request.form['Age'])
                db.session.add(NewCustomer)
                db.session.commit()
                return render_template('AddCust.html', PrintAllCustomer = Customers.query.all())
            else:
                return render_template('Eror.html')
        return render_template('AddCust.html', PrintAllCustomer = Customers.query.all())

@app.route('/addBook/', methods=['POST', 'GET'])
def AddBook():
    if request.method == 'POST':
        if  1 <= int(request.form['Type']) <= 3:
            NewBook = Books(NameBook=request.form['NameBook'],
                                Author = request.form['Author'], YearPublished =request.form['YearPublished'],
                                Type = request.form['Type'])
            db.session.add(NewBook)
            db.session.commit()
            return render_template('ShowAllBooks.html', PrintAllBook = Books.query.all())
        else:
            return render_template('Eror.html')
    return render_template('AddBook.html')

@app.route('/PrintAll/<customername>', methods=['GET','POST'])
@app.route('/PrintAll/', methods=['GET','POST'])
def PrintAllCustomer(customername=''):
    if request.method == 'POST':
        for name in Customers.query.all():
            if request.form.get("SerachCust").title() == name.Name:
                customername = name.Name
                return render_template('personalCust.html', customername = customername, PrintAllCustomer= Customers.query.all())
        return render_template('ShowAllCust.html', PrintAllCustomer = Customers.query.all())
    else:
        return render_template('ShowAllCust.html', PrintAllCustomer = Customers.query.all())


@app.route('/Book/<bookname>', methods=['GET'])
@app.route('/Book/', methods=['GET', 'POST'])
def PrintAllBook(bookname=''):
    if request.method == 'POST':
        for OneBook in Books.query.all():
            if request.form.get("SerachBook").title() == OneBook.NameBook:
                bookname = OneBook.NameBook
                return render_template('personalBook.html', bookname=bookname, PrintAllBook=Books.query.all())
    return render_template('ShowAllBooks.html', PrintAllBook = Books.query.all())


@app.route("/deleteCustomer/<id>", methods=['DELETE', 'GET'])
def deleteCustomer(id=0):
        customerID=Customers.query.get(int(id))
        custInLoan=Loans.query.all()
        for id_cust in custInLoan:
            return render_template('Eror.html')
        else: 
            db.session.delete(customerID)
            db.session.commit()
        return render_template('ShowAllCust.html', PrintAllCustomer = Customers.query.all())

@app.route("/deleteBook/<id>",methods=['DELETE','GET'])
def deleteBook(id=0):
    book = Books.query.get(id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return render_template('ShowAllBooks.html', book = Books.query.all())
    return f"the id book doesn't exist"

@app.route("/AddLoan/", methods=['GET', 'POST'])
def AddLoan():
    dayLoan = datetime.utcnow().date()
    id_cust = (request.form.get('CustID'))
    for id in Customers.query.all():
        if request.method == 'POST':
            if (int(id_cust) == id.CusomerID):
                for book in Books.query.filter_by(NameBook=request.form.get("bookname")):
                    if book.Type == 1:
                        ReturnDate = dayLoan + timedelta(days=10)
                    elif book.Type == 2:
                        ReturnDate = dayLoan + timedelta(days=5)
                    else:
                        ReturnDate = dayLoan + timedelta(days=2)
                    NewLoans = Loans(CusomerID=request.form['CustID'],
                                    BookId=book.BookId, LoanDate=dayLoan,
                                    ReturnDate=ReturnDate)
                    db.session.add(NewLoans)
                    db.session.commit()
                    return render_template('ShowAllLoan.html', AllLoanBook=Loans.query.all()) 
            else:
                return render_template('Eror.html')
    return render_template('FormLoan.html', Onlybook = Books.query.all())

@app.route("/AllLoans/",methods=['GET'])
def AllLoanBook():
    return render_template('ShowAllLoan.html', AllLoanBook=Loans.query.all())

@app.route("/ReturnBook/<LoansID>", methods=['DELETE', 'GET'])
def ReturnBook(LoansID=0):
        DeleteFromDB = Loans.query.get(int(LoansID))
        if int(LoansID) > 0:
            db.session.delete(DeleteFromDB)
            db.session.commit()
            return render_template('ShowAllLoan.html', AllLoanBook=Loans.query.all()) 
        return render_template('Eror.html')

@app.route("/lateLoans/", methods = ['GET'])
def late():
    results = []
    table_loan = Loans.query.all()
    for date in table_loan:
        if date.ReturnDate < datetime.utcnow().date():
            results.append(date)
    return render_template('LateLoan.html', results = results)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

