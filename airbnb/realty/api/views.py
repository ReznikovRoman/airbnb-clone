from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from hosts.models import RealtyHost
from .serializers import RealtySerializer, RealtyUpdateSerializer
from ..services.realty import get_all_available_realty


class RealtyListApiView(generics.ListCreateAPIView):
    """
    get:
    Return a list of all available Realty objects.

    post:
    Create a new Realty object.
    """
    queryset = get_all_available_realty()
    serializer_class = RealtySerializer

    def post(self, request: Request, *args, **kwargs):
        # TODO: set realty host properly (another issue - DRF authentication, authorization)
        host_pk = RealtyHost.objects.first().pk
        request.data['host_pk'] = host_pk
        request.data['host'] = {'user': {'profile': {}}}

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(host_pk=host_pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RealtyDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    retrieve:
    Return a Realty object by the given id.

    put:
    Update some of the Realty object's fields.

    delete:
    Delete a Realty object by the given id.
    """
    queryset = get_all_available_realty()
    serializer_class = RealtyUpdateSerializer
