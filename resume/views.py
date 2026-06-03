# file: resume/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from django.db.models import Prefetch
from landing_spot.models import User, Skill, SkillCategory, Project


def pdf_resume_view(request, username, action):
    # Get the user
    person = get_object_or_404(User, username=username)

    # Get the active resume
    resume = person.resumes.filter(is_active=True).first()
    if not resume:
        return HttpResponse("No active resume found for this user.", status=404)

    # Get categorized skills
    skill_categories = SkillCategory.objects.prefetch_related(
        Prefetch('skills', queryset=Skill.objects.filter(user=person))
    ).filter(skills__user=person).distinct()

    # Resume projects
    projects = Project.objects.filter(
        resume_project__resume=resume
    ).order_by('-resume_project__hierarchy')

    # Experiences and education
    experiences = person.experiences.all()
    educations = person.educations.all()

    # Prepare template context
    context = {
        'person': person,
        'resume': resume,
        'skill_categories': skill_categories,
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
    }

    # Render HTML string from template
    html_string = render_to_string('resume_pdf.html', context)

    # Generate PDF using WeasyPrint
    # pdf_file = HTML(string=html_string).write_pdf()
    pdf_file = HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')  # Root URL so media/static paths work
    ).write_pdf()


    # Set the correct response type
    if action == 'download':
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{person.username}_resume.pdf"'
    elif action == 'view':
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="resume.pdf"'
    else:
        return HttpResponse("Invalid action.", status=400)

    return response

