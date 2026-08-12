from django.core.exceptions import (
    ImproperlyConfigured,
    ValidationError as DjangoValidationError,
    ObjectDoesNotExist,
    MultipleObjectsReturned,
    FieldError,
)
from django.db import IntegrityError, DatabaseError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

def drf_exception_handler(exc, context):
    # Django ValidationError (from model.clean(), etc.)
    if isinstance(exc, DjangoValidationError):
        detail = exc.message_dict if hasattr(exc, 'message_dict') else {'non_field_errors': [str(exc)]}
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)
    
    # Django ObjectDoesNotExist (should be 404)
    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            {'detail': 'Requested object does not exist.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Django FieldError (bad query)
    if isinstance(exc, FieldError):
        return Response(
            {'detail': f'Invalid field in query: {str(exc)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Database integrity errors (duplicate keys, etc.)
    if isinstance(exc, IntegrityError):
        return Response(
            {'detail': 'Database integrity error. Duplicate or invalid data.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Database errors (connection issues, etc.)
    if isinstance(exc, DatabaseError):
        return Response(
            {'detail': 'Database error occurred. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # ImproperlyConfigured
    if isinstance(exc, ImproperlyConfigured):
        return Response(
            {'detail': f'Configuration error: {str(exc)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Handle Http404 from Django
    if isinstance(exc, Http404):
        return Response(
            {'detail': 'Not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Let DRF handle everything else
    return exception_handler(exc, context)