"""
Standardized API response helpers for consistent response formatting.
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional


def api_success(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    **extra_fields
) -> Response:
    """
    Return a standardized success response.
    
    Args:
        data: The data to return in the response
        message: Success message
        status_code: HTTP status code (default: 200)
        **extra_fields: Additional fields to include in response
        
    Returns:
        Response: DRF Response object with standardized format
        
    Example:
        return api_success(
            data={'user': user_data},
            message="User created successfully",
            status_code=status.HTTP_201_CREATED
        )
    """
    response_data = {
        'success': True,
        'message': message,
    }
    
    if data is not None:
        response_data['data'] = data
    
    response_data.update(extra_fields)
    
    return Response(response_data, status=status_code)


def api_error(
    message: str = "An error occurred",
    errors: Optional[Any] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    **extra_fields
) -> Response:
    """
    Return a standardized error response.
    
    Args:
        message: Error message
        errors: Detailed error information (e.g., validation errors)
        status_code: HTTP status code (default: 400)
        **extra_fields: Additional fields to include in response
        
    Returns:
        Response: DRF Response object with standardized format
        
    Example:
        return api_error(
            message="Validation failed",
            errors={'email': ['This field is required']},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    """
    response_data = {
        'success': False,
        'message': message,
    }
    
    if errors is not None:
        response_data['errors'] = errors
    
    response_data.update(extra_fields)
    
    return Response(response_data, status=status_code)

