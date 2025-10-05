from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from base.models import Program
from api.serializers.program_serializer import ProgramSerializer


# Helper to format serializer errors
def format_serializer_errors(errors):
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted


# --------------------------
# GET (List) + POST (Create)
# --------------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def program_list(request):
    if request.method == "GET":
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = ProgramSerializer(data=request.data)
        if serializer.is_valid():
            try:
                program = serializer.save()
                return Response(
                    {"status": "success", "data": ProgramSerializer(program).data},
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "Program with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"status": "error", "message": format_serializer_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST
            )


# --------------------------
# GET (Retrieve) + PUT (Update) + DELETE
# --------------------------
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def program_detail(request, pk):
    try:
        program = Program.objects.get(pk=pk)
    except Program.DoesNotExist:
        return Response(
            {"status": "error", "message": "Program not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # GET - Retrieve
    if request.method == "GET":
        serializer = ProgramSerializer(program)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    # PUT - Update
    elif request.method == "PUT":
        serializer = ProgramSerializer(program, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"status": "success", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "Program with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"status": "error", "message": format_serializer_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST
            )

    # DELETE - Delete
    elif request.method == "DELETE":
        program.delete()
        return Response(
            {"status": "success", "message": "Program deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
