from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, AllowAny

from base.models import Contractor
from api.serializers.contractor_serializers import ContractorSerializer


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def contractor_list_create(request):

    if request.method == "GET":
        contractors = Contractor.objects.filter().order_by("name")
        serializer = ContractorSerializer(contractors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        serializer = ContractorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Contractor created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def contractor_detail(request, pk):

    try:
        contractor = Contractor.objects.get(pk=pk)
    except Contractor.DoesNotExist:
        return Response(
            {"error": "Contractor not found."},
            status=status.HTTP_404_NOT_FOUND
        )


    if request.method == "GET":
        serializer = ContractorSerializer(contractor)
        return Response(serializer.data, status=status.HTTP_200_OK)


    if request.method == "PUT":
        serializer = ContractorSerializer(contractor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Contractor updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    if request.method == "PATCH":
        serializer = ContractorSerializer(contractor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Contractor partially updated!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "DELETE":
        contractor.delete()
        return Response(
            {"message": "Contractor deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
