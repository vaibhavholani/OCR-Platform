from flask import Blueprint, jsonify, request
from .. import db
from ..models import User

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'count': len(users)
    })

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User with this email already exists'}), 400
    
    user = User(
        name=data['name'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@bp.route('/<int:user_id>/documents', methods=['GET'])
def get_user_documents(user_id):
    """Get all documents for a user"""
    user = User.query.get_or_404(user_id)
    documents = user.documents.all()
    return jsonify({
        'documents': [doc.to_dict() for doc in documents],
        'count': len(documents)
    })

@bp.route('/<int:user_id>/templates', methods=['GET'])
def get_user_templates(user_id):
    """Get all templates for a user"""
    user = User.query.get_or_404(user_id)
    templates = user.templates.all()
    return jsonify({
        'templates': [template.to_dict() for template in templates],
        'count': len(templates)
    }) 