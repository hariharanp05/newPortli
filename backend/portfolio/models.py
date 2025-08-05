from mongoengine import *
from users.models import User  # adjust path as needed

class Education(EmbeddedDocument):
    degree = StringField()
    institution = StringField()
    start_year = StringField()
    end_year = StringField()
    description = StringField()

class Experience(EmbeddedDocument):
    title = StringField()
    company = StringField()
    start_date = StringField()
    end_date = StringField()
    description = StringField()

class Skill(EmbeddedDocument):
    skill = StringField()
    level = StringField()

class Project(EmbeddedDocument):
    title = StringField()
    description = StringField()
    tech_stack = StringField()
    live_link = StringField()
    repo_link = StringField()

class Certification(EmbeddedDocument):
    title = StringField()
    issuer = StringField()
    date = StringField()
    description = StringField()

class Portfolio(Document):
    user = ReferenceField(User, required=True, unique=True)
    
    # Basic Info
    full_name = StringField()
    title = StringField()
    profile_image = StringField()
    short_bio = StringField()
    email = StringField()
    phone = StringField()

    # About & Social
    about_me = StringField()
    social_links = DictField()  # linkedin, github, twitter, etc.

    # Main Sections
    education = ListField(EmbeddedDocumentField(Education))
    experience = ListField(EmbeddedDocumentField(Experience))
    skills = ListField(EmbeddedDocumentField(Skill))
    projects = ListField(EmbeddedDocumentField(Project))
    certifications = ListField(EmbeddedDocumentField(Certification))

    # Contact Preferences
    show_email = BooleanField(default=True)
    show_contact_form = BooleanField(default=True)
    contact_message = StringField()

    # Layout & Theme
    layout = DictField()  # store layout style, line type, theme, colors, fonts, bg image

    meta = {'collection': 'portfolio'}
