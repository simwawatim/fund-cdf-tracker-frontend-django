from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import responses
from api.serializers.program_serializer import ProgramSerializer
from rest_framework import status
from base.models import Program


def format_serializer_errors(errors):
    formatted = {}
    for field, value in errors.items():
        if isinstance(value, list):
            formatted[field] = [str(v) for v in value]
        else:
            formatted[field] = str(value)
    return formatted


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def program_list(request):
    if request.method == "GET":
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
    elif request.method == "POST":
        serializer = ProgramSerializer(data = request.data)
        if serializer.is_valid():
            try:
                program= serializer.save()
                return Response({"status": "success", "data": ProgramSerializer(program).data},
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"status": "error", "message": "Username or email already exists."},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"status": "error", "message": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "message": format_serializer_errors(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)
