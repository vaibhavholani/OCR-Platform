from flask import Blueprint, request, jsonify
from ..services import CreditService

credit_bp = Blueprint('credits', __name__, url_prefix='/api/credits')

@credit_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_credits(user_id):
    """Get comprehensive user credit information"""
    credit_summary = CreditService.get_user_credit_summary(user_id)
    
    if not credit_summary:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'data': credit_summary
    })

@credit_bp.route('/user/<int:user_id>/add', methods=['POST'])
def add_credits(user_id):
    """Add credits to user account"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    amount = data.get('amount')
    description = data.get('description', 'Manual credit addition')
    
    if not amount or not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Invalid amount. Must be positive integer.'}), 400
    
    success, message, transaction_info = CreditService.add_credits_to_user(
        user_id, amount, description
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'transaction': transaction_info,
            'user_summary': CreditService.get_user_credit_summary(user_id)
        })
    else:
        return jsonify({'error': message}), 400

@credit_bp.route('/user/<int:user_id>/check', methods=['POST'])
def check_credits_for_operation(user_id):
    """Check if user has sufficient credits for an operation"""
    data = request.get_json()
    required_credits = data.get('amount', 1) if data else 1
    
    if not isinstance(required_credits, int) or required_credits <= 0:
        return jsonify({'error': 'Invalid amount. Must be positive integer.'}), 400
    
    success, message, user_info = CreditService.check_user_credits(user_id, required_credits)
    
    return jsonify({
        'success': True,
        'has_sufficient_credits': success,
        'message': message,
        'user_info': user_info
    })

@credit_bp.route('/document/<int:doc_id>/usage', methods=['GET'])
def get_document_credit_usage(doc_id):
    """Get credit usage information for a specific document"""
    usage_info = CreditService.get_document_credit_usage(doc_id)
    
    if not usage_info:
        return jsonify({
            'success': True,
            'message': 'No credit usage found for this document',
            'data': None
        })
    
    return jsonify({
        'success': True,
        'data': usage_info
    })

@credit_bp.route('/admin/users', methods=['GET'])
def get_all_users_credit_summary():
    """Admin route to get credit summary for all users"""
    try:
        from ..models import User
        users = User.query.all()
        
        summary = []
        for user in users:
            user_summary = CreditService.get_user_credit_summary(user.user_id)
            if user_summary:
                summary.append({
                    'user_id': user.user_id,
                    'name': user.name,
                    'email': user.email,
                    'credits_remaining': user.credits_remaining,
                    'plan_type': user.plan_type,
                    'total_transactions': user.credit_transactions.count(),
                    'total_spent': user_summary['credits']['total_spent'],
                    'total_added': user_summary['credits']['total_added']
                })
        
        return jsonify({
            'success': True,
            'data': summary,
            'total_users': len(users)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving admin summary: {str(e)}'}), 500
