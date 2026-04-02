import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from unidecode import unidecode
from .models import Exam, Quiz, Question, Choice


@login_required
def exam_list(request):
    exams = Exam.objects.annotate(quiz_count=Count('quizzes')).all()
    context = {'exams': exams}
    return render(request, 'quiz/exam_list.html', context)


@login_required
def quiz_list(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    quizzes = exam.quizzes.annotate(question_count=Count('questions')).all()
    context = {'exam': exam, 'quizzes': quizzes}
    return render(request, 'quiz/quiz_list.html', context)


@login_required
def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question_ids = list(quiz.questions.values_list('id', flat=True))
    random.shuffle(question_ids)
    question_ids = question_ids[:50]

    prefix = f'quiz_{quiz_id}'
    request.session[f'{prefix}_ids'] = question_ids
    request.session[f'{prefix}_answers'] = {}
    return redirect('quiz_question', quiz_id=quiz_id, index=0)


@login_required
def quiz_question(request, quiz_id, index):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    ids = request.session.get(f'quiz_{quiz_id}_ids', [])
    if not ids or index >= len(ids):
        return redirect('quiz_result', quiz_id=quiz_id)

    question = get_object_or_404(Question, pk=ids[index])
    answers = request.session.get(f'quiz_{quiz_id}_answers', {})
    selected_choice_id = answers.get(str(ids[index]))

    context = {
        'quiz': quiz,
        'question': question,
        'index': index,
        'total': len(ids),
        'is_last': index == len(ids) - 1,
        'selected_choice_id': int(selected_choice_id) if selected_choice_id else None,
    }
    return render(request, 'quiz/quiz_question.html', context)


@require_POST
def check_answer(request):
    choice_id = request.POST.get('choice_id')
    quiz_id = request.POST.get('quiz_id')
    q_id = request.POST.get('question_id')

    if not choice_id:
        return JsonResponse({})

    choice = get_object_or_404(Choice, pk=int(choice_id))
    question = choice.question

    if quiz_id:
        key = f'quiz_{quiz_id}_answers'
        answers = request.session.get(key, {})
        answers[str(q_id)] = choice_id
        request.session[key] = answers

    data = {
        'is_correct': choice.is_correct,
        'explanation': question.explanation or '',
    }
    if not choice.is_correct:
        correct = question.choices.filter(is_correct=True).first()
        data['correct_answer_text'] = correct.text if correct else ''
    return JsonResponse(data)


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    ids = request.session.get(f'quiz_{quiz_id}_ids', [])
    answers = request.session.get(f'quiz_{quiz_id}_answers', {})

    score = 0
    results = []
    for q_id in ids:
        try:
            question = Question.objects.get(pk=q_id)
            correct = question.choices.filter(is_correct=True).first()
            user_choice = None
            is_correct = False
            chosen_id = answers.get(str(q_id))
            if chosen_id:
                user_choice = Choice.objects.get(pk=int(chosen_id))
                is_correct = user_choice.is_correct
                if is_correct:
                    score += 1
            results.append({'question': question, 'user_choice': user_choice,
                            'correct_choice': correct, 'is_correct': is_correct})
        except (Question.DoesNotExist, Choice.DoesNotExist):
            continue

    context = {
        'quiz': quiz,
        'score': score,
        'total': len(ids),
        'results': results,
    }
    return render(request, 'quiz/quiz_result.html', context)


@login_required
def quiz_review(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    ids = request.session.get(f'quiz_{quiz_id}_ids', [])
    answers = request.session.get(f'quiz_{quiz_id}_answers', {})

    questions_status = []
    for i, q_id in enumerate(ids):
        questions_status.append({
            'index': i,
            'number': i + 1,
            'answered': str(q_id) in answers,
        })

    answered_count = sum(1 for q in questions_status if q['answered'])
    unanswered_count = len(questions_status) - answered_count

    context = {
        'quiz': quiz,
        'questions_status': questions_status,
        'answered_count': answered_count,
        'unanswered_count': unanswered_count,
        'total': len(ids),
    }
    return render(request, 'quiz/quiz_review.html', context)


@login_required
def question_lookup(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = []
    query = ""

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            search_term = unidecode(query.lower())
            questions = Question.objects.filter(
                Q(quiz__exam_id=exam_id) & (
                    Q(search_acronym__istartswith=search_term) |
                    Q(search_text_normalized__icontains=search_term)
                )
            ).prefetch_related('choices').distinct()

    context = {'exam': exam, 'questions': questions, 'query': query}
    return render(request, 'quiz/question_lookup.html', context)
