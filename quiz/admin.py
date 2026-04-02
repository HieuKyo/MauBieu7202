import pandas as pd
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Exam, Quiz, Question, Choice, _generate_acronym
from .forms import QuestionImportForm
from unidecode import unidecode


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
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz__exam', 'quiz')
    search_fields = ('text',)
    change_list_template = "admin/quiz/question/change_list.html"

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

                    questions_to_create = []
                    temp_choice_data = []

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
                        question = Question(
                            quiz=quiz,
                            text=text,
                            order=order_int,
                            explanation=str(row.get(7, '')) if pd.notna(row.get(7, '')) else '',
                            search_acronym=_generate_acronym(text),
                            search_text_normalized=unidecode(text.lower()),
                        )
                        questions_to_create.append(question)

                        choices_text = [row.get(2), row.get(3), row.get(4), row.get(5)]
                        try:
                            correct_answer_index = int(row.get(6, 0)) if pd.notna(row.get(6, 0)) else 0
                        except (ValueError, TypeError):
                            correct_answer_index = 0
                        temp_choice_data.append((choices_text, correct_answer_index))

                    created_questions = Question.objects.bulk_create(questions_to_create)

                    if len(created_questions) != len(temp_choice_data):
                        raise Exception("Lỗi đồng bộ: Số lượng câu hỏi tạo ra không khớp với dữ liệu lựa chọn.")

                    choices_to_create = []
                    for question, choice_data in zip(created_questions, temp_choice_data):
                        choices_text, correct_index = choice_data
                        for i, choice_text in enumerate(choices_text, 1):
                            if pd.notna(choice_text):
                                choices_to_create.append(
                                    Choice(
                                        question=question,
                                        text=str(choice_text),
                                        is_correct=(i == correct_index)
                                    )
                                )

                    Choice.objects.bulk_create(choices_to_create)

                    self.message_user(
                        request,
                        f"Import thành công {len(created_questions)} câu hỏi vào đề thi '{quiz.title}'.",
                        messages.SUCCESS
                    )
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
