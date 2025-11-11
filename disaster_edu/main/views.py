from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import QuizResult
from django.shortcuts import redirect



def home(request):
    return render(request, 'main/home.html')

def awareness(request):
    disasters = [
        {"name": "Earthquake", "image": "main/images/earthquake.jpg"},
        {"name": "Fire", "image": "main/images/fire.jpg"},
        {"name": "Flood", "image": "main/images/flood.jpg"},
        {"name": "Cyclone", "image": "main/images/cyclone.jpg"},
        {"name": "Landslide", "image": "main/images/landslide.jpg"},
        {"name": "Pandemic", "image": "main/images/pandemic.jpg"},
    ]
    return render(request, 'main/awareness.html', {'disasters': disasters})


def disaster_detail(request, disaster_name):
    details = {
        "Earthquake": {
            "image": "main/images/earthquake.jpg",
            "tips": [
                "Drop, cover, and hold on during shaking.",
                "Stay away from windows and heavy furniture.",
                "Move to an open area once shaking stops."
            ],
        },
        "Fire": {
            "image": "main/images/fire.jpg",
            "tips": [
                "Stay low to avoid smoke.",
                "Use stairs, not elevators, during fire evacuation.",
                "Have an extinguisher and smoke alarm at home."
            ],
        },
        "Flood": {
            "image": "main/images/flood.jpg",
            "tips": [
                "Move to higher ground immediately.",
                "Avoid walking or driving through floodwaters.",
                "Keep emergency supplies and clean water ready."
            ],
        },
        "Cyclone": {
            "image": "main/images/cyclone.jpg",
            "tips": [
                "Secure windows and doors before the storm hits.",
                "Move to designated shelters when advised.",
                "Keep a battery-powered radio for updates."
            ],
        },
        "Landslide": {
            "image": "main/images/landslide.jpg",
            "tips": [
                "Stay alert for unusual sounds or ground movement.",
                "Avoid building houses near steep slopes.",
                "Move away quickly from the path of a landslide."
            ],
        },
        "Pandemic": {
            "image": "main/images/pandemic.jpg",
            "tips": [
                "Wash hands frequently and wear masks in public.",
                "Avoid crowded places and maintain social distance.",
                "Follow government health advisories."
            ],
        },
    }

    disaster = details.get(disaster_name.title(), None)
    if not disaster:
        return render(request, 'main/404.html', status=404)

    return render(request, 'main/disaster_detail.html', {
        'name': disaster_name.title(),
        'image': disaster["image"],
        'tips': disaster["tips"],
    })


def tips(request):
    return render(request, 'main/tips.html')


def quiz(request):
    questions = [
        {'id': 1, 'question': 'What should you do during an earthquake?', 
         'options': ['Run outside immediately', 'Take cover under a desk', 'Stand near windows', 'Use elevators'], 
         'answer': 'Take cover under a desk'},
        {'id': 2, 'question': 'What is the emergency helpline number in India?', 
         'options': ['100', '101', '108', '112'], 
         'answer': '112'},
        {'id': 3, 'question': 'Which color flag indicates cyclone warning?', 
         'options': ['Green', 'Yellow', 'Red', 'Blue'], 
         'answer': 'Red'},
    ]

    results = None
    if request.method == 'POST':
        results = []
        score = 0
        for q in questions:
            selected = request.POST.get(f'question_{q["id"]}')
            correct = (selected == q['answer'])
            results.append({'question': q['question'], 'selected': selected,
                            'correct': q['answer'], 'is_correct': correct})
            if correct:
                score += 1
        total = len(questions)
        percentage = int((score / total) * 100)

        # ✅ Save to QuizResult if user is authenticated student
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.role == 'student':
                QuizResult.objects.create(user=request.user, score=score)

        return render(request, 'main/quiz.html',
                      {'results': results, 'score': score, 'total': total, 'percentage': percentage})

    return render(request, 'main/quiz.html', {'questions': questions})




def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        try:
            send_mail(
                subject=f"New Message from {name}",
                message=f"Email: {email}\n\nMessage:\n{message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['info@disasteredu.org'],
                fail_silently=False,
            )
            messages.success(request, "✅ Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, "❌ There was an issue sending your message. Please try again.")
        
        return redirect('contact')
    return render(request, 'main/contact.html')





from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import QuizResult

@login_required
def teacher_dashboard(request):
    if request.user.profile.role != 'teacher':
        return redirect('home')
    
    results = QuizResult.objects.all().select_related('user').order_by('-date_taken')

    # Filtering by student
    student_id = request.GET.get('student')
    if student_id:
        results = results.filter(user__id=student_id)
    
    # Sorting
    sort = request.GET.get('sort')
    if sort == 'score':
        results = results.order_by('-score')
    elif sort == 'date':
        results = results.order_by('-date_taken')

    # Pagination
    paginator = Paginator(results, 10)  # 10 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get list of students for filter dropdown
    students = QuizResult.objects.values_list('user__id', 'user__username').distinct()

    # Get Top 5 students by score (latest attempt)
    top_students = (
        QuizResult.objects.order_by('-score', '-date_taken')
        .select_related('user')[:5]
    )

    return render(request, 'main/teacher_dashboard.html', {
        'results': page_obj,
        'students': students,
        'student_id': student_id,
        'sort': sort,
        'top_students': top_students,  # new
    })

