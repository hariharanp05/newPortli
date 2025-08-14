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
        user_obj = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        portfolio = Portfolio.objects.get(user=user_obj.id)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Public portfolio not found'}, status=status.HTTP_404_NOT_FOUND)

    # Convert ObjectId to string for JSON
    portfolio_data = convert_objectid(portfolio.to_mongo().to_dict())
    return Response(portfolio_data, status=status.HTTP_200_OK)
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portfolio(request):
    user = request.user

    # Prevent duplicate portfolio
    if Portfolio.objects(user=user).first():
        return Response({'error': 'Portfolio already exists'}, status=400)

    data = request.data
    try:
        portfolio = Portfolio(
            user=user,
            full_name=data.get('full_name'),
            title=data.get('title'),
            profile_image=data.get('profile_image'),
            short_bio=data.get('short_bio'),
            email=data.get('email'),
            phone=data.get('phone'),
            about_me=data.get('about_me'),
            social_links=data.get('social_links', {}),
            education=data.get('education', []),
            experience=data.get('experience', []),
            skills=data.get('skills', []),
            projects=data.get('projects', []),
            certifications=data.get('certifications', []),
            show_email=data.get('show_email', True),
            show_contact_form=data.get('show_contact_form', True),
            contact_message=data.get('contact_message'),
            layout=data.get('layout', {}),
        )
        portfolio.save()
        return Response({'message': 'Portfolio created'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio_by_user(request):
    user = request.user
    portfolio = Portfolio.objects(user=user).first()
    if not portfolio:
        return Response(None, status=200)
    portfolio_json = json.loads(portfolio.to_json())
    return Response(portfolio_json, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_portfolio(request, portfolio_id):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=404)

    data = request.data

    # Update fields
    
    # Normal fields
    for field in ['full_name', 'title', 'profile_image', 'short_bio', 'email', 'phone',
                  'about_me', 'social_links', 'show_email', 'show_contact_form', 'contact_message', 'layout']:
        if field in data:
            setattr(portfolio, field, data[field])

    # Embedded fields
    if 'education' in data:
        portfolio.education = [Education(**edu) for edu in data['education']]

    if 'experience' in data:
        portfolio.experience = [Experience(**exp) for exp in data['experience']]

    if 'skills' in data:
        portfolio.skills = [Skill(**sk) for sk in data['skills']]

    if 'projects' in data:
        portfolio.projects = [Project(**proj) for proj in data['projects']]

    if 'certifications' in data:
        portfolio.certifications = [Certification(**cert) for cert in data['certifications']]


    portfolio.save()
    return Response({'message': 'Portfolio updated successfully'}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_portfolio(request, portfolio_id):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        portfolio.delete()
        return Response({'message': 'Portfolio deleted'}, status=200)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=404)
