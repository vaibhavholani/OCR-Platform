from flask import Blueprint, jsonify, request
from flask import current_app
from .. import db
from ..models import Template, TemplateField, SubTemplateField, FieldOption, SubTemplateFieldOption
from ..utils.enums import FieldType, FieldName, DataType
from ..tally import auto_load_tally_options, auto_load_tally_sub_field_options, TallyFieldOptionsError, refresh_field_options

bp = Blueprint('templates', __name__, url_prefix='/api/templates')

@bp.route('/', methods=['GET'])
def get_templates():
    """Get all templates"""
    templates = Template.query.all()
    return jsonify({
        'templates': [template.to_dict() for template in templates],
        'count': len(templates)
    })

@bp.route('/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template by ID"""

    template_fields = TemplateField.query.filter_by(template_id=template_id).all()

    select_fields = [f for f in template_fields if f.field_type == FieldType.SELECT]
    for select_field in select_fields:
        try:
            refresh_result = refresh_field_options(select_field.field_id)
            print(f"Refreshed {refresh_result.get('options_count', 0)} options for field '{select_field.field_name.value}'")
        except TallyFieldOptionsError as e:
            print(f"Warning: Failed to refresh options for field '{select_field.field_name.value}': {e}")
            # Continue processing even if refresh fails
        except Exception as e:
            print(f"Warning: Unexpected error refreshing field '{select_field.field_name.value}': {e}")
            # Continue processing even if refresh fails
    
    # Also refresh SELECT sub-fields in table fields
    table_fields_for_refresh = [f for f in template_fields if f.field_type == FieldType.TABLE]
    for table_field in table_fields_for_refresh:
        sub_fields = SubTemplateField.query.filter_by(field_id=table_field.field_id).all()
        select_sub_fields = [sf for sf in sub_fields if sf.data_type == DataType.SELECT]
        for select_sub_field in select_sub_fields:
            try:
                # Use the sub-field auto-load function
                refresh_result = auto_load_tally_sub_field_options(select_sub_field.sub_temp_field_id)
                print(f"Refreshed {refresh_result.get('options_count', 0)} options for sub-field '{select_sub_field.field_name.value}'")
            except TallyFieldOptionsError as e:
                print(f"Warning: Failed to refresh options for sub-field '{select_sub_field.field_name.value}': {e}")
            except Exception as e:
                print(f"Warning: Unexpected error refreshing sub-field '{select_sub_field.field_name.value}': {e}")

    template = Template.query.get_or_404(template_id)
    return jsonify(template.to_dict())

@bp.route('/names', methods=['GET'])
def get_template_names():
    """Get only template names and IDs"""
    templates = Template.query.all()
    return jsonify({
        'templates': [{'temp_id': template.temp_id, 'name': template.name} for template in templates],
        'count': len(templates)
    })

@bp.route('/', methods=['POST'])
def create_template():
    """Create a new template"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('user_id', 'name')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    template = Template(
        user_id=data['user_id'],
        name=data['name'],
        description=data.get('description'),
        ai_instructions=data.get('ai_instructions')
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify(template.to_dict()), 201

@bp.route('/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update a template"""
    template = Template.query.get_or_404(template_id)
    data = request.get_json()
    
    if 'name' in data:
        template.name = data['name']
    if 'description' in data:
        template.description = data['description']
    if 'ai_instructions' in data:
        template.ai_instructions = data['ai_instructions']
    
    db.session.commit()
    return jsonify(template.to_dict())

@bp.route('/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    template = Template.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return jsonify({'message': 'Template deleted successfully'})

@bp.route('/<int:template_id>/fields', methods=['GET'])
def get_template_fields(template_id):
    """Get all fields for a template"""
    template = Template.query.get_or_404(template_id)
    fields = template.template_fields.all()
    return jsonify({
        'template_fields': [field.to_dict() for field in fields],
        'count': len(fields)
    })

@bp.route('/<int:template_id>/fields', methods=['POST'])
def create_template_field(template_id):
    """Create a template field"""
    template = Template.query.get_or_404(template_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('field_name', 'field_order', 'field_type')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        field_name = FieldName(data['field_name'].lower())
        field_type = FieldType(data['field_type'].lower())
    except ValueError as e:
        return jsonify({'error': f'Invalid field name or type: {str(e)}'}), 400
    
    field = TemplateField(
        template_id=template_id,
        field_name=field_name,
        field_order=data['field_order'],
        field_type=field_type,
        ai_instructions=data.get('ai_instructions')
    )
    
    db.session.add(field)
    db.session.commit()
    
    # Optionally auto-load Tally options for SELECT fields
    try:
        if field.field_type == FieldType.SELECT:
            try:
                auto_load_tally_options(field.field_id, clear_existing=True)
            except TallyFieldOptionsError as e:
                current_app.logger.warning(f"Auto-load Tally options failed for field {field.field_id}: {e}")
    except Exception:
        # Non-fatal: ensure API response is returned even if logging fails
        pass

    return jsonify(field.to_dict()), 201

@bp.route('/fields/<int:field_id>', methods=['GET'])
def get_template_field(field_id):
    """Get a specific template field"""
    field = TemplateField.query.get_or_404(field_id)
    return jsonify(field.to_dict())

@bp.route('/fields/<int:field_id>', methods=['PUT'])
def update_template_field(field_id):
    """Update a template field"""
    field = TemplateField.query.get_or_404(field_id)
    data = request.get_json()
    
    try:
        if 'field_name' in data:
            field.field_name = FieldName(data['field_name'].lower())
        if 'field_order' in data:
            field.field_order = data['field_order']
        if 'field_type' in data:
            field.field_type = FieldType(data['field_type'].lower())
        if 'ai_instructions' in data:
            field.ai_instructions = data['ai_instructions']
    except ValueError as e:
        return jsonify({'error': f'Invalid field name or type: {str(e)}'}), 400
    
    db.session.commit()
    return jsonify(field.to_dict())

@bp.route('/fields/<int:field_id>', methods=['DELETE'])
def delete_template_field(field_id):
    """Delete a template field"""
    field = TemplateField.query.get_or_404(field_id)
    db.session.delete(field)
    db.session.commit()
    return jsonify({'message': 'Template field deleted successfully'})

@bp.route('/fields/<int:field_id>/sub-fields', methods=['GET'])
def get_sub_template_fields(field_id):
    """Get sub fields for a template field"""
    field = TemplateField.query.get_or_404(field_id)
    sub_fields = field.sub_template_fields.all()
    return jsonify({
        'sub_template_fields': [sub_field.to_dict() for sub_field in sub_fields],
        'count': len(sub_fields)
    })

@bp.route('/fields/<int:field_id>/sub-fields', methods=['POST'])
def create_sub_template_field(field_id):
    """Create a sub template field"""
    field = TemplateField.query.get_or_404(field_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('field_name', 'data_type')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        field_name = FieldName(data['field_name'].lower())
        data_type = DataType(data['data_type'].lower())
    except ValueError as e:
        return jsonify({'error': f'Invalid field name or data type: {str(e)}'}), 400
    
    sub_field = SubTemplateField(
        field_id=field_id,
        field_name=field_name,
        data_type=data_type,
        ai_instructions=data.get('ai_instructions')
    )
    
    db.session.add(sub_field)
    db.session.commit()
    
    # Optionally auto-load Tally options for SELECT sub-fields
    try:
        if sub_field.data_type == DataType.SELECT:
            try:
                auto_load_tally_sub_field_options(sub_field.sub_temp_field_id, clear_existing=True)
            except TallyFieldOptionsError as e:
                current_app.logger.warning(f"Auto-load Tally options failed for sub-field {sub_field.sub_temp_field_id}: {e}")
    except Exception:
        pass

    return jsonify(sub_field.to_dict()), 201

@bp.route('/fields/<int:field_id>/options', methods=['GET'])
def get_field_options(field_id):
    """Get options for a template field"""
    field = TemplateField.query.get_or_404(field_id)
    options = field.field_options.all()
    return jsonify({
        'field_options': [option.to_dict() for option in options],
        'count': len(options)
    })

@bp.route('/fields/<int:field_id>/options', methods=['POST'])
def create_field_option(field_id):
    """Create a field option"""
    field = TemplateField.query.get_or_404(field_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ('option_value', 'option_label')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    option = FieldOption(
        field_id=field_id,
        option_value=data['option_value'],
        option_label=data['option_label']
    )
    
    db.session.add(option)
    db.session.commit()
    
    return jsonify(option.to_dict()), 201 

# Sub-Template Field Option endpoints
@bp.route('/sub-fields/<int:sub_field_id>/options', methods=['GET'])
def get_sub_field_options(sub_field_id):
    """Get options for a sub-template field"""
    sub_field = SubTemplateField.query.get_or_404(sub_field_id)
    options = sub_field.sub_field_options.all()
    return jsonify({
        'sub_field_options': [option.to_dict() for option in options],
        'count': len(options)
    })

@bp.route('/sub-fields/<int:sub_field_id>/options', methods=['POST'])
def create_sub_field_option(sub_field_id):
    """Create a sub-template field option"""
    sub_field = SubTemplateField.query.get_or_404(sub_field_id)
    
    # Validate that sub-field is SELECT type
    if sub_field.data_type != DataType.SELECT:
        return jsonify({'error': 'Sub-field must be of SELECT type to have options'}), 400
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ('option_value', 'option_label')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    option = SubTemplateFieldOption(
        sub_temp_field_id=sub_field_id,
        option_value=data['option_value'],
        option_label=data['option_label']
    )
    
    db.session.add(option)
    db.session.commit()
    
    return jsonify(option.to_dict()), 201

@bp.route('/sub-fields/options/<int:option_id>', methods=['DELETE'])
def delete_sub_field_option(option_id):
    """Delete a sub-template field option"""
    option = SubTemplateFieldOption.query.get_or_404(option_id)
    db.session.delete(option)
    db.session.commit()
    return jsonify({'message': 'Sub-field option deleted successfully'})