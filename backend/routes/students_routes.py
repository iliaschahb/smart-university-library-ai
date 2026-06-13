from flask import Blueprint, jsonify, request
from database import db
from models import Student, User

students_bp = Blueprint("students_bp", __name__)


def student_to_dict(student):
    return {
        "id": student.id,
        "user_id": student.user_id,
        "full_name": student.full_name,
        "email": student.email,
        "department": student.department,
        "level": student.level,
        "created_at": student.created_at.isoformat() if student.created_at else None
    }


@students_bp.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([student_to_dict(student) for student in students]), 200


@students_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Étudiant introuvable"}), 404

    return jsonify(student_to_dict(student)), 200


@students_bp.route("/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    full_name = data.get("full_name")
    email = data.get("email")
    department = data.get("department")
    level = data.get("level")
    password_hash = data.get("password_hash", "hashed_default_password")

    if not full_name or not email:
        return jsonify({"error": "Les champs full_name et email sont obligatoires"}), 400

    existing_user = User.query.filter_by(email=email).first()
    existing_student = Student.query.filter_by(email=email).first()

    if existing_user or existing_student:
        return jsonify({"error": "Un utilisateur ou étudiant avec cet email existe déjà"}), 400

    new_user = User(
        name=full_name,
        email=email,
        password_hash=password_hash,
        role="etudiant"
    )

    db.session.add(new_user)
    db.session.commit()

    new_student = Student(
        user_id=new_user.id,
        full_name=full_name,
        email=email,
        department=department,
        level=level
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({
        "message": "Étudiant ajouté avec succès",
        "student": student_to_dict(new_student)
    }), 201


@students_bp.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Étudiant introuvable"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    new_email = data.get("email", student.email)

    # Vérification doublon email sur un autre étudiant
    existing_student = Student.query.filter(
        Student.email == new_email,
        Student.id != student.id
    ).first()

    if existing_student:
        return jsonify({"error": "Un autre étudiant utilise déjà cet email"}), 400

    user = User.query.get(student.user_id)
    if user:
        existing_user = User.query.filter(
            User.email == new_email,
            User.id != user.id
        ).first()

        if existing_user:
            return jsonify({"error": "Un autre utilisateur utilise déjà cet email"}), 400

    student.full_name = data.get("full_name", student.full_name)
    student.email = new_email
    student.department = data.get("department", student.department)
    student.level = data.get("level", student.level)

    if user:
        user.name = student.full_name
        user.email = new_email

    db.session.commit()

    return jsonify({
        "message": "Étudiant mis à jour avec succès",
        "student": student_to_dict(student)
    }), 200


@students_bp.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Étudiant introuvable"}), 404

    user = User.query.get(student.user_id)

    db.session.delete(student)

    if user:
        db.session.delete(user)

    db.session.commit()

    return jsonify({"message": "Étudiant supprimé avec succès"}), 200
