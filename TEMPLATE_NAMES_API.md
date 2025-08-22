# New Template Names API Endpoints

## Overview
Added two new API endpoints that return only template names and IDs, providing a lightweight alternative to the full template endpoints.

## New Endpoints

### 1. Global Template Names
**`GET /api/templates/names`**

Returns only template names and IDs for all templates.

**Response:**
```json
{
  "count": 2,
  "templates": [
    {
      "temp_id": 1,
      "name": "Sample Invoice Template"
    },
    {
      "temp_id": 2,
      "name": "Purchase Order Template"
    }
  ]
}
```

### 2. User-Specific Template Names
**`GET /api/users/{user_id}/templates/names`**

Returns only template names and IDs for a specific user's templates.

**Response:**
```json
{
  "count": 1,
  "templates": [
    {
      "temp_id": 1,
      "name": "Sample Invoice Template"
    }
  ]
}
```

## Benefits

### Data Size Comparison
- **Full Template API**: ~548 characters per template (includes all fields, metadata, template_fields array)
- **Names Only API**: ~49 characters per template (91% reduction in data size)

### Use Cases
- **Dropdown/Select Components**: Perfect for populating template selection dropdowns
- **Template Listing**: Quick template lists without loading full configuration
- **Performance**: Faster loading for UI components that only need names
- **Bandwidth**: Reduced network usage, especially with many templates

## Code Structure
Following the existing patterns:
- Same response format structure (`templates` array + `count`)
- Same error handling (404 for invalid user_id)
- Same route naming conventions
- Consistent with existing API design

## Files Modified
1. `/app/api/template_routes.py` - Added global template names endpoint
2. `/app/api/user_routes.py` - Added user-specific template names endpoint

## Testing
Both endpoints tested successfully:
- ✅ Global endpoint: `GET /api/templates/names`
- ✅ User endpoint: `GET /api/users/1/templates/names`
- ✅ Response format consistent with existing APIs
- ✅ Performance improvement verified
