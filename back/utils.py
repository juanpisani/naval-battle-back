import string
import time
import random

from django.db.models import Func
from rest_framework import pagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from server import settings
User = get_user_model()


def log_message(thing, message):
    """:returns: detailed error message using reflection"""
    return '{} {}'.format(repr(thing), message)


class LogUtilMixin(object):

    def log(self, message):
        """:returns: Log message formatting"""
        if message is None:
            message = ''

        return log_message(thing=self, message=message)


def get_non_field_error(message):

    return {
        'non_field_errors': [
            message
        ]
    }


class CustomPageNumberPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current': self.page.number,
            'results': data
        })

    def get_page_size(self, request):
        if 'page_size' in request.query_params:
            if int(request.query_params['page_size']) > 0:
                return request.query_params['page_size']
            return None
        return self.page_size

    def get_next_link(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        return page_number

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        return page_number


def get_default_admin_user():
    return User.objects.filter(is_staff=1).order_by('id').first()


def millis():
    return int(round(time.time() * 1000))


class Round(Func):
    function = 'ROUND'
    arity = 2


def random_string(string_length):
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(string_length))

# def cell_to_pos(cell):
#