import os

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import desc, asc
# Hier werden die Datenbank Uebertragung definiert.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@db:5432/pa_vcid_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '*?K+RQkz^DVfaD<7'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.app_context().push()

def user_has_liked(post, user_id):
    return any(like.user_id == user_id for like in post.likes)


app.jinja_env.filters['user_has_liked'] = user_has_liked


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    friends = db.relationship('Friendship', foreign_keys='Friendship.user_id',
                              backref=db.backref('user_friends', lazy=True), lazy=True)
    friend_of = db.relationship('Friendship', foreign_keys='Friendship.friend_id',
                                backref=db.backref('friend_of', lazy=True), lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

    def __repr__(self):
        return f"Post('{self.content}', '{self.author.username}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def get_username(self):
        user = User.query.get(self.user_id)
        return user.username if user else 'Unknown'

    def __repr__(self):
        return f"Comment('{self.content}', '{self.user.username}')"


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, unique=True)

    def __repr__(self):
        return f"Like('{self.user_id}', '{self.post_id}')"


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Friendship('{self.user.username}', '{self.friend.username}')"


@app.before_request
def before_request():
    # Pruefen, ob der Benutzer angemeldet ist.
    if request.endpoint == 'register':
        return
    elif "application/json" in request.headers.get('Accept'):
        try:
            username = request.authorization.username
            password = request.authorization.password
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                return
        except AttributeError:
            return jsonify({'error': 'Unauthorized'}), 401
    elif 'user_id' not in session and request.endpoint not in ['login', 'register']:
        return redirect(url_for('login'))


@app.route('/')
def home():
    # Sortierparameter aus dem Query-String abrufen
    sort_by = request.args.get('sort_by', 'date')  # Standardmaessig wird nach Datum sortiert

    # Abrufen von Beitraegen anhand des Sortierparameters
    if sort_by == 'likes_desc':
        posts = Post.query.outerjoin(Like).group_by(Post.id).order_by(desc(db.func.count(Like.id)))
    elif sort_by == 'likes_asc':
        posts = Post.query.outerjoin(Like).group_by(Post.id).order_by(asc(db.func.count(Like.id)))
    else:
        # Standardsortierung nach Datum
        posts = Post.query.order_by(Post.id.desc()).all()

    user = get_user(request)

    if user:
        friend_ids = user.friends
        friend_of_ids = user.friend_of
        friends = [User.query.get(friend.friend_id) for friend in friend_ids]
        friends.extend([User.query.get(friend.user_id) for friend in friend_of_ids])

        if "application/json" in request.headers.get('Accept'):
            posts_json = [{'content': post.content, 'author': post.author.username} for post in posts]
            return jsonify({'posts': posts_json, 'friends': [friend.username for friend in friends]}), 200

        return render_template('home.html', posts=posts, friends=friends, username=user.username)
    else:
        if 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'error': 'User not found'}), 404
        else:
            flash('User not found.', 'danger')
            return render_template('home.html', posts=posts)

# Beitraege erstellen.
@app.route('/create_post', methods=['POST'])
def create_post():
    # if 'user_id' in Sitzung:
    user = get_user(request)

    if user:
        post_content = request.form.get('post_content')
        new_post = Post(content=post_content, author=user)
        db.session.add(new_post)
        db.session.commit()
        flash('Beitrag erfolgreich erstellt!', 'success')
        if "application/json" in request.headers.get('Accept'):
            return jsonify({'content': post_content, 'author': user.username}), 200
    else:
        flash('User not found.', 'danger')
    # else:
    #     flash('Bitte melden Sie sich an, um einen Beitrag zu erstellen.', 'danger')

    return redirect(url_for('home'))

# Like geben.
@app.route('/add_like/<int:post_id>', methods=['POST'])
def add_like(post_id):
    # if 'user_id' in Sitzung:
    user = get_user(request)
    post = Post.query.get(post_id)

    if not post or not user:
        flash('Invalid post or user.', 'danger')
    else:
        try:
            existing_like = Like.query.filter_by(user_id=user.id, post_id=post_id).first()

            if existing_like:
                # Unlike: Benutzer hat den Beitrag bereits geliked, also entfernen Sie das Like
                db.session.delete(existing_like)
                flash('Like entfernt!', 'success')
                if "application/json" in request.headers.get('Accept'):
                    # Gibt die Anzahl der Likes fuer den Beitrag zurueck
                    db.session.commit()
                    return jsonify({'likes': len(post.likes)}), 200
            else:
                # Like: Benutzer hat den Beitrag nicht gemocht, also fuegen Sie das Like hinzu.
                new_like = Like(user_id=user.id, post_id=post_id)
                db.session.add(new_like)
                flash('Like hinzugefuegt.!', 'success')
                if "application/json" in request.headers.get('Accept'):
                    # Gibt die Anzahl der Likes fuer den Beitrag zurueck
                    db.session.commit()
                    return jsonify({'likes': len(post.likes)}), 200

            db.session.commit()

        except IntegrityError:
            # Dies fuehrt zu einem IntegrityError, wenn ein Benutzer versucht, denselben Beitrag zweimal zu moegen
            db.session.rollback()
            flash('Sie haben diesen Beitrag bereits gemocht.', 'danger')

    # else: flash('Bitte loggen Sie sich ein, um einen Beitrag zu moegen oder nicht zu moegen.', 'danger')

    return redirect(url_for('home'))

# Kommentieren hinzufuegen.
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    # if 'user_id' in Sitzung:
    user = get_user(request)

    if user:
        comment_content = request.form.get('content')
        new_comment = Comment(content=comment_content, user_id=user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Kommentar hinzugefuegt!', 'success')
        if "application/json" in request.headers.get('Accept'):
            return jsonify({'content': comment_content, 'author': user.username}), 200
    else:
        flash('Benutzer nicht gefunden.', 'danger')
    # else: flash('Bitte loggen Sie sich ein, um Beitraege zu kommentieren.', 'danger')

    return redirect(url_for('home'))


@app.route('/search_users', methods=['POST'])
def search_users():
    # 'user_id' in Sitzung:
    search_username = request.form.get('search_username')
    users = User.query.filter(User.username.ilike(f'%{search_username}%')).all()

    if "application/json" in request.headers.get('Accept'):
        users_json = [{'username': user.username} for user in users]
        return jsonify({'users': users_json}), 200

    return render_template('search_users.html', users=users, search_query=search_username)

    # flash('Bitte melden Sie sich an, um nach Benutzern zu suchen.', 'danger')
    # Rueckleitung(url_for('home'))


@app.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    # 'user_id' in Sitzung:
    user = get_user(request)
    user_id = user.id

    if user_id == friend_id:
        flash('Sie koennen sich selbst nicht als Freund hinzufuegen.', 'danger')
    elif Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first() or Friendship.query.filter_by(
            user_id=friend_id, friend_id=user_id).first():
        flash('Sie sind bereits mit diesem Benutzer befreundet.', 'info')
    else:
        new_friendship = Friendship(user_id=user_id, friend_id=friend_id)
        db.session.add(new_friendship)
        db.session.commit()
        flash('Freundschaftsanfrage gesendet!', 'success')
        if "application/json" in request.headers.get('Accept'):
            return jsonify({'friend_id': friend_id}), 200

    return redirect(url_for('home'))

# Registierung Vorgang
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash('Benutzername oder E-Mail existiert bereits. Bitte versuchen Sie es erneut.', 'danger')
            return render_template('register.html')

        flash('Ihr Konto wurde erstellt!', 'success')

        if "application/json" in request.headers.get('Accept'):
            return jsonify({'username': username, 'email': email}), 200

        return redirect(url_for('login'))

    return render_template('register.html')

# Login Vorgang
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            flash('Anmeldung erfolgreich!', 'success')
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Login fehlgeschlagen. Bitte ueberpruefen Sie Ihren Benutzernamen und Ihr Passwort.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Implementierung einer Abmeldefunktion, falls erforderlich
    session.pop('user_id', None)
    flash('Sie wurden abgemeldet.', 'success')
    return redirect(url_for('home'))


def get_user(req):
    if 'application/json' not in req.headers.get('Accept'):
        user_id = session['user_id']
        user = User.query.get(user_id)
    else:
        username = req.authorization.username
        user = User.query.filter_by(username=username).first()
    return user

    # Externe URL 
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
