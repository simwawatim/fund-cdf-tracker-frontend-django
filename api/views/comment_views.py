from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from api.serializers.comment_serializers import ProjectCommentSerializer
from base.models import ProjectComment


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def project_comments_list_create(request):
    if request.method == 'GET':
        project_id = request.query_params.get('project')
        qs = ProjectComment.objects.filter(is_active=True)
        if project_id:
            qs = qs.filter(project_id=project_id)
        serializer = ProjectCommentSerializer(qs, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ProjectCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Allow user from request data
            return Response({
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.AllowAny])
def project_comment_detail(request, pk):
    try:
        comment = ProjectComment.objects.get(pk=pk, is_active=True)
    except ProjectComment.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Comment not found."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectCommentSerializer(comment)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectCommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        comment.is_active = False
        comment.save()
        return Response({
            "status": "success",
            "message": "Comment deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)
