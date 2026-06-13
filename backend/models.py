from datetime import datetime
from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="user", uselist=False)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(100))
    level = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship("Loan", backref="student", lazy=True)
    ratings = db.relationship("Rating", backref="student", lazy=True)
    recommendations = db.relationship("Recommendation", backref="student", lazy=True)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    books = db.relationship("Book", backref="category", lazy=True)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150))
    isbn = db.Column(db.String(50), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    publication_year = db.Column(db.Integer)
    average_rating = db.Column(db.Float, default=0)
    ratings_count = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    available_quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship("Loan", backref="book", lazy=True)
    ratings = db.relationship("Rating", backref="book", lazy=True)
    recommendations = db.relationship("Recommendation", backref="book", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "publication_year": self.publication_year,
            "average_rating": self.average_rating,
            "ratings_count": self.ratings_count,
            "quantity": self.quantity,
            "available_quantity": self.available_quantity
        }


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default="BORROWED", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    algorithm = db.Column(db.String(100), default="popularity_based")
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
