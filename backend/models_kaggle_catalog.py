from datetime import datetime, date

from database import db


class BooksCatalog(db.Model):
    __tablename__ = "books_catalog"

    book_id = db.Column(db.Integer, primary_key=True)  # book_id from Goodbooks / aggregated work-level id
    goodreads_book_id = db.Column(db.BigInteger, index=True)
    best_book_id = db.Column(db.BigInteger)
    work_id = db.Column(db.BigInteger)
    isbn = db.Column(db.String(64))
    isbn13 = db.Column(db.String(32), index=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    authors = db.Column(db.String(500), nullable=False)
    publication_year = db.Column(db.Integer)
    language_code = db.Column(db.String(32))
    average_rating = db.Column(db.Float, default=0)
    ratings_count = db.Column(db.Integer, default=0)
    work_ratings_count = db.Column(db.Integer, default=0)
    work_text_reviews_count = db.Column(db.Integer, default=0)
    image_url = db.Column(db.Text)
    small_image_url = db.Column(db.Text)
    data_source = db.Column(db.String(32), default="kaggle_goodbooks")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    analytics = db.relationship(
        "BookAnalytics",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
    )
    inventory = db.relationship(
        "Inventory",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
    )
    loans = db.relationship("LoanLocal", back_populates="book")


class BookAnalytics(db.Model):
    __tablename__ = "book_analytics_rel"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books_catalog.book_id"), unique=True, nullable=False, index=True)
    top_tags_json = db.Column(db.Text)
    global_popularity_score = db.Column(db.Float, default=0)
    global_popularity_level = db.Column(db.String(32), default="faible")
    avg_user_rating = db.Column(db.Float, default=0)
    to_read_count = db.Column(db.Integer, default=0)
    tag_count = db.Column(db.Integer, default=0)
    local_loan_count = db.Column(db.Integer, default=0)
    local_active_loan_count = db.Column(db.Integer, default=0)
    local_late_count = db.Column(db.Integer, default=0)
    demand_score = db.Column(db.Float, default=0)
    recommended_stock = db.Column(db.Integer, default=0)
    last_sync_at = db.Column(db.DateTime, default=datetime.utcnow)

    book = db.relationship("BooksCatalog", back_populates="analytics")


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books_catalog.book_id"), unique=True, nullable=False, index=True)
    quantity = db.Column(db.Integer, default=0)
    available_quantity = db.Column(db.Integer, default=0)
    shelf_location = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    book = db.relationship("BooksCatalog", back_populates="inventory")


class StudentLocal(db.Model):
    __tablename__ = "students_rel"

    student_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    department = db.Column(db.String(120))
    level = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship("LoanLocal", back_populates="student")


class LoanLocal(db.Model):
    __tablename__ = "loans_rel"

    loan_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students_rel.student_id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books_catalog.book_id"), nullable=False, index=True)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="BORROWED", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("StudentLocal", back_populates="loans")
    book = db.relationship("BooksCatalog", back_populates="loans")

    @property
    def is_late(self):
        return self.return_date is None and self.due_date < date.today()
