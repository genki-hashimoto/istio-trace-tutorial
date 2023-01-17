from django.http import HttpResponse

import requests

from django.conf import settings

from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span, span_in_context

tracing = settings.OPENTRACING_TRACING


def index(request):
    if validate(request.GET):
        value = request.GET.get("value")
    else:
        value = "Hello world."

    return HttpResponse(value)


def trace(request):
    headers = get_forward_headers(request.headers)
    response = requests.get(settings.REQUEST_URL, headers=headers, params={'value': 'from_a'})

    return HttpResponse("app say: " + response.text)


def validate(get):
    if "value" in get:
        return True
    else:
        return False


def get_forward_headers(current_headers):
    # x-b3-*** headers can be populated using the opentracing span
    span = get_current_span()
    carrier = {}
    tracing.tracer.inject(
        span_context=span.context,
        format=Format.HTTP_HEADERS,
        carrier=carrier)

    incoming_headers = [
        'x-request-id',
        'x-b3-traceid',
        'x-b3-spanid',
        'x-b3-parentspanid',
        'x-b3-sampled',
        'x-b3-flags',
    ]
    for ihdr in incoming_headers:
        val = current_headers.get(ihdr)
        if val is not None:
            carrier[ihdr] = val

    return carrier
