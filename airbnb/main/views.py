from django.shortcuts import render
from django.http import HttpRequest


def index(request: HttpRequest):
    turn_on_block = False
    return render(
        request,
        'index.html',
        context={
            'turn_on_block': turn_on_block,
        }
    )
