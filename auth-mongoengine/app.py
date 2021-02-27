from flask import Flask, url_for, redirect, render_template, request
from flask_mongoengine import MongoEngine

# from wtforms import form, fields, validators


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

from flask_admin import Admin,BaseView,AdminIndexView
from flask_login import UserMixin,current_user,LoginManager,login_user,logout_user,UserMixin

from flask_admin.contrib.mongoengine import ModelView
# from flask_admin import Helpers

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# MongoDB settings
app.config['MONGODB_SETTINGS'] = {'DB': 'test'}
db = MongoEngine(app)
# db.init_app(app)


# Create user model. For simplicity, it will store passwords in plain text.
# Obviously that's not right thing to do in real world application.
class User(db.Document):
    login = db.StringField(max_length=80, unique=True)
    email = db.StringField(max_length=120)
    password = db.StringField(max_length=64)
    #is_active = Required(bool)
    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.login


# Define login and registration forms (for flask-login)
class LoginForm(FlaskForm):
    login = StringField(validators=[DataRequired()])
    password =PasswordField(validators=[DataRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            #raise ValidationError('Invalid user')
            print("'Invalid user'")
        if user.password != self.password:
            #raise ValidationError('Invalid password')
            print("'Invalid password'")

    def get_user(self):
        return User(login=self.login,password=self.password)


class RegistrationForm(FlaskForm):
    login = StringField(validators=[DataRequired()])
    password =PasswordField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])

    def validate_login(self, field):
        if User(login=self.login.data):
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager =LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User(id=user_id)


# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        return  True#current_user.is_authenticated() ###?????????????????????


# Create customized index view class
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return True#current_user.is_authenticated()       ######?????????????


# Flask views
@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()

        form.populate_obj(user)
        user.save()

        login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize flask-login
    init_login()

    # Create admin
    admin = Admin(app, 'Example: Auth-Mongo', index_view=MyAdminIndexView())

    # Add view
    admin.add_view(MyModelView(User))

    # Start app
    app.run(debug=True)
