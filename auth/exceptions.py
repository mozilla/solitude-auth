from django.http import HttpResponse


class MissingDestination(Exception):
    status = 422


class ExceptionMiddleware(object):

    def process_exception(self, request, exception):
        status = getattr(exception, 'status', None)
        if status:
            return HttpResponse(status=status)
