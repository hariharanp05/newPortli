from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Portfolio, Education, Experience, Skill, Project, Certification
import json
from django.http import JsonResponse
from users.models import User 
from bson import ObjectId
from rest_framework import status

# Helper function to convert ObjectId to string
def convert_objectid(data):
    if isinstance(data, dict):
        return {k: convert_objectid(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_portfolio(request, username):
    """
    Public read-only endpoint to fetch a portfolio by username.
    No authentication required.
    """
    
    
    # try:
    #     portfolio = Portfolio.objects.get(user__username=username)
    # except Portfolio.DoesNotExist:
    #     return Response({'error': 'Portfolio not found'}, status=404)

    # # Convert to JSON
    # portfolio_json = json.loads(portfolio.to_json())

    # # Apply privacy settings
    # if not portfolio_json.get('show_email', True):
    #     portfolio_json.pop('email', None)

    # if not portfolio_json.get('show_contact_form', True):
    #     portfolio_json.pop('contact_message', None)
    #     portfolio_json.pop('phone', None)

    # return Response(portfolio_json, status=200)


    try:
        # Directly fetch portfolio using username
        portfolio = Portfolio.objects.get(username=username)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Public portfolio not found'}, status=status.HTTP_404_NOT_FOUND)

    # Convert ObjectId to string for JSON
    portfolio_data = convert_objectid(portfolio.to_mongo().to_dict())
    return Response(portfolio_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_portfolio(request):
    user_id = str(request.user.id)
    data = request.data
    user = request.user

    try:
        # This will update if portfolio exists, otherwise create new one
        portfolio = Portfolio.objects(user_id=user_id).modify(
            upsert=True,           # create if not exists
            new=True,              # return the new doc
            set__username=user.username, 
            set__full_name=data.get('full_name'),
            set__title=data.get('title'),
            set__profile_image=data.get('profile_image'),
            set__short_bio=data.get('short_bio'),
            set__email=data.get('email'),
            set__phone=data.get('phone'),
            set__about_me=data.get('about_me'),
            set__social_links=data.get('social_links', {}),
            set__education=data.get('education', []),
            set__experience=data.get('experience', []),
            set__skills=data.get('skills', []),
            set__projects=data.get('projects', []),
            set__certifications=data.get('certifications', []),
            set__show_email=data.get('show_email', True),
            set__show_contact_form=data.get('show_contact_form', True),
            set__contact_message=data.get('contact_message'),
            set__layout=data.get('layout', {}),
        )
        portfolio.save()
        return Response({'message': 'Portfolio saved successfully'}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio_by_user(request):
    user_id = str(request.user.id)
    portfolio = Portfolio.objects(user_id=user_id).first()
    if not portfolio:
        return Response({'error': 'Portfolio not found'}, status=404)

    # Convert to dict and fix ObjectId
    data = portfolio.to_mongo().to_dict()
    data['_id'] = str(data['_id'])   # make JSON serializable

    return Response(data, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_portfolio(request, user_id):
    user_id = str(request.user.id)
    try:
        portfolio = Portfolio.objects.get(user_id=user_id)
        portfolio.delete()
        return Response({'message': 'Portfolio deleted'}, status=200)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=404)
