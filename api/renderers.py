from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Default response structure
        response = {
            'status': 'success',
            'message': '',
            'data': None
        }

        # Handle errors: When `data` contains errors or status code >= 400
        if renderer_context['response'].status_code >= 400:
            response['status'] = 'error'
            # Extract error message (flatten non-field errors if any)
            response['message'] = self.extract_error_message(data)
            response['data'] = None
        else:
            # Success responses
            response['data'] = data

            # Check for custom messages passed via the view
            if 'message' in renderer_context.get('response', {}):
                response['message'] = renderer_context['response'].data.get('message', '')

            # Handle ListSerializer responses (multiple objects)
            if isinstance(data, list):
                response['message'] = 'Data retrieved successfully'
            # Handle DictSerializer or single object responses
            elif isinstance(data, dict):
                response['message'] = 'Operation successful'

        # Render the final response
        return super().render(response, accepted_media_type, renderer_context)

    def extract_error_message(self, data):
        """Extract and return the first error message from the data."""

        # Case 1: Direct error messages (e.g., from the `detail` key or simple error string)
        if isinstance(data, dict):
            if 'detail' in data:
                return data['detail']

            # Loop through dictionary to find the first error
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        # Handle nested dictionaries for non-field errors
                        if isinstance(item, dict):
                            nested_error = self.extract_error_message(item)
                            if nested_error:
                                # For 'non_field_errors', return just the message
                                return nested_error if key == 'non_field_errors' else f"{key}: {nested_error}"
                        # If it's a string, treat it as a direct error message
                        elif isinstance(item, str):
                            return item if key == 'non_field_errors' else f"{key}: {item}"
                # Handle nested dictionary errors recursively
                elif isinstance(value, dict):
                    nested_error = self.extract_error_message(value)
                    if nested_error:
                        return nested_error if key == 'non_field_errors' else f"{key}: {nested_error}"
                # If the value is a direct string error (common in validation)
                elif isinstance(value, str):
                    return value if key == 'non_field_errors' else f"{key}: {value}"

        # Case 2: Handle lists of strings (common in non-field errors)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    return item

        # Case 3: Fallback to a default message if no error is found
        return



