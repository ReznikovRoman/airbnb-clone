from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from ..filters import RealtyFilter
from ..services.realty import get_all_available_realty
from .permissions import IsAbleToAddRealty, IsRealtyOwnerOrReadOnly
from .serializers import RealtySerializer, RealtyUpdateSerializer


class RealtyListApiView(generics.ListCreateAPIView):
    """API view for listing realty objects.

    get:
    Return a list of all available Realty objects.

    post:
    Create a new Realty object.
    """

    queryset = get_all_available_realty()
    serializer_class = RealtySerializer
    filterset_class = RealtyFilter
    permission_classes = (
        IsAbleToAddRealty,
    )

    def post(self, request: Request, *args, **kwargs):
        host_pk = request.user.host.id
        request.data['host_pk'] = host_pk
        request.data['host'] = {'user': {'profile': {}}}

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(host_pk=host_pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RealtyDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """API view for a single Realty object.

    retrieve:
    Return a Realty object by the given id.

    put:
    Update some of the Realty object's fields.

    delete:
    Delete a Realty object by the given id.
    """

    queryset = get_all_available_realty()
    serializer_class = RealtyUpdateSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsRealtyOwnerOrReadOnly,
    )
