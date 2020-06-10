import string
import time
import random

import numpy as np
from django.db.models import Func
from rest_framework import pagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from back.models import Cell
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


ROW_MAP = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7,
    'I': 8,
    'J': 9,
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'E',
    5: 'F',
    6: 'G',
    7: 'H',
    8: 'I',
    9: 'J',
}

# fila x columna


def dict_to_board(board):
    list_cells = []
    result = np.empty((10, 10), dtype=Cell)
    for i in range(len(board)):
        extreme1 = board[i]['extreme1']
        extreme2 = board[i]['extreme2']
        lower = extreme1
        higher = extreme2
        # caso {extreme1: A1, extreme2: A1}
        if extreme1 == extreme2:
            result[ROW_MAP[extreme1[0]]][int(extreme1[1:]) - 1] = Cell(True).toJSON()
            list_cells.append((ROW_MAP[extreme1[0]],int(extreme1[1:]) - 1))
        # caso {extreme1: A1, extreme2: A4}
        elif extreme1[0] == extreme2[0]:
            if extreme1[1:] > extreme2[1:]:
                lower = extreme2
                higher = extreme1
            for j in range(int(lower[1:]) - 1, int(higher[1:])):
                result[ROW_MAP[lower[0]]][j] = Cell(True).toJSON()
                list_cells.append(ROW_MAP[lower[0]],j)
        else:
            # caso {extreme1: C5, extreme2: F5}
            if ROW_MAP[extreme1[0]] > ROW_MAP[extreme2[0]]:
                lower = extreme2
                higher = extreme1
            for j in range(ROW_MAP[lower[0]], ROW_MAP[higher[0]] + 1):
                result[j][int(lower[1:]) - 1] = Cell(True).toJSON()
                list_cells.append(j, int(lower[1:]) - 1)
    for i in range(0, 10):
        for j in range(0, 10):
            if result[i][j] is None:
                result[i][j] = Cell(False).toJSON()
    return result, list_cells
