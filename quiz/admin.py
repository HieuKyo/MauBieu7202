import pandas as pd
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Exam, Quiz, Question, Choice
from .forms import QuestionImportForm
from unidecode import unidecode


def _dup_key(normalized):
    return " ".join((normalized or "").split())


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam', 'created_at')
    list_filter = ('exam',)
    search_fields = ('title',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'quiz_titles', 'order')
    list_filter = ('quizzes__exam', 'quizzes')
    filter_horizontal = ('quizzes',)
    search_fields = ('text',)
    change_list_template = "admin/quiz/question/change_list.html"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('quizzes')

    @admin.display(description="Đề thi")
    def quiz_titles(self, obj):
        return ", ".join(q.title for q in obj.quizzes.all())

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.admin_site.admin_view(self.import_questions_view), name='quiz_question_import'),
        ]
        return custom_urls + urls

    def import_questions_view(self, request):
        if request.method == "POST":
            form = QuestionImportForm(request.POST, request.FILES)
            if form.is_valid():
                quiz = form.cleaned_data['quiz']
                file = request.FILES['file']
                try:
                    df = pd.read_excel(file, header=None)

                    # Ngân hàng câu hỏi chung: kiểm tra trùng trên toàn bộ các kỳ thi/đề thi
                    existing = {
                        _dup_key(q.search_text_normalized): q
                        for q in Question.objects.order_by('id')
                    }

                    # Gom dữ liệu theo câu hỏi; trùng trong file thì dòng sau ghi đè dòng trước
                    rows = {}
                    for index, row in df.iterrows():
                        question_text = row.get(1)
                        if pd.isna(question_text) or not question_text:
                            continue

                        # Bỏ qua dòng tiêu đề nếu cột A không phải số
                        order_val = row.get(0, index + 1)
                        try:
                            order_int = int(order_val)
                        except (ValueError, TypeError):
                            continue

                        text = str(question_text)
                        try:
                            correct_answer_index = int(row.get(6, 0)) if pd.notna(row.get(6, 0)) else 0
                        except (ValueError, TypeError):
                            correct_answer_index = 0
                        rows[_dup_key(unidecode(text.lower()))] = {
                            'text': text,
                            'order': order_int,
                            'explanation': str(row.get(7, '')) if pd.notna(row.get(7, '')) else '',
                            'choices': [row.get(2), row.get(3), row.get(4), row.get(5)],
                            'correct': correct_answer_index,
                        }

                    created_count = updated_count = 0
                    with transaction.atomic():
                        for key, data in rows.items():
                            question = existing.get(key)
                            if question:
                                # Trùng câu hỏi cũ -> ưu tiên dữ liệu mới nhất
                                question.text = data['text']
                                question.order = data['order']
                                question.explanation = data['explanation']
                                question.save()
                                question.choices.all().delete()
                                updated_count += 1
                            else:
                                question = Question.objects.create(
                                    text=data['text'],
                                    order=data['order'],
                                    explanation=data['explanation'],
                                )
                                created_count += 1
                            question.quizzes.add(quiz)

                            for i, choice_text in enumerate(data['choices'], 1):
                                if pd.notna(choice_text):
                                    Choice.objects.create(
                                        question=question,
                                        text=str(choice_text),
                                        is_correct=(i == data['correct']),
                                    )

                    msg = f"Import vào đề thi '{quiz.title}': thêm mới {created_count} câu hỏi"
                    if updated_count:
                        msg += f", cập nhật {updated_count} câu hỏi đã có trong ngân hàng (lấy theo dữ liệu mới nhất)"
                    self.message_user(request, msg + ".", messages.SUCCESS)
                    return redirect("..")

                except Exception as e:
                    self.message_user(request, f"Lỗi khi đọc file: {e}", messages.ERROR)
        else:
            form = QuestionImportForm()

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'form': form,
            'title': "Import Câu hỏi từ Excel",
        }
        return render(request, "admin/quiz/question/import_questions.html", context)
