# mixins.py
from rest_framework.response import Response
from rest_framework import status


class PrototypeMixin:
    """
    A quick way to test APIView responses and routing.
    Returns basic info for common HTTP methods.
    Usage:
        class TestView(PrototypeMixin, APIView):
        pass
    """

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "method": "GET",
                "path": request.path,
                "query_params": request.query_params,
                "kwargs": kwargs,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        return Response(
            {
                "method": "POST",
                "path": request.path,
                "data": request.data,
                "kwargs": kwargs,
            },
            status=status.HTTP_201_CREATED,
        )

    def put(self, request, *args, **kwargs):
        return Response(
            {
                "method": "PUT",
                "path": request.path,
                "data": request.data,
                "kwargs": kwargs,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        return Response(
            {
                "method": "DELETE",
                "path": request.path,
                "kwargs": kwargs,
            },
            status=status.HTTP_204_NO_CONTENT,
        )
