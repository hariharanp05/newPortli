from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio
from users.models import User
import datetime

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
    return Response(portfolio.to_mongo().to_dict(), status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_portfolio(request, portfolio_id):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=404)

    data = request.data

    # Update fields
    for field in ['full_name', 'title', 'profile_image', 'short_bio', 'email', 'phone',
                  'about_me', 'social_links', 'education', 'experience', 'skills', 'projects',
                  'certifications', 'show_email', 'show_contact_form', 'contact_message', 'layout']:
        if field in data:
            setattr(portfolio, field, data[field])

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
