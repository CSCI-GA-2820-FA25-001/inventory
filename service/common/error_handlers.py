######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Module: error_handlers
"""
from flask import current_app as app
from service.models import DataValidationError
from . import status
from service.routes import api


######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles DataValidationError"""
    return bad_request(error)


@api.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """Handles 400 Bad Request"""
    message = str(error)
    app.logger.warning(message)
    return (
        {
            "status": status.HTTP_400_BAD_REQUEST,
            "error": "Bad Request",
            "message": message,
        },
        status.HTTP_400_BAD_REQUEST,
    )


@api.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Handles 404 Not Found"""
    message = str(error)
    app.logger.warning(message)
    return (
        {
            "status": status.HTTP_404_NOT_FOUND,
            "error": "Not Found",
            "message": message,
        },
        status.HTTP_404_NOT_FOUND,
    )


@api.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """Handles 405 Method Not Allowed"""
    message = str(error)
    app.logger.warning(message)
    return (
        {
            "status": status.HTTP_405_METHOD_NOT_ALLOWED,
            "error": "Method Not Allowed",
            "message": message,
        },
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@api.errorhandler(status.HTTP_409_CONFLICT)
def conflict(error):
    """Handles 409 Conflict"""
    message = str(error)
    app.logger.warning(message)
    return (
        {
            "status": status.HTTP_409_CONFLICT,
            "error": "Conflict",
            "message": message,
        },
        status.HTTP_409_CONFLICT,
    )


@api.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """Handles 415 Unsupported Media Type"""
    message = str(error)
    app.logger.warning(message)
    return (
        {
            "status": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "error": "Unsupported media type",
            "message": message,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@api.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Handles 500 Internal Server Error"""
    message = str(error)
    app.logger.error(message)
    return (
        {
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Internal Server Error",
            "message": message,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
