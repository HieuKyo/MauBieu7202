from django import forms
from .models import Quiz


class QuestionImportForm(forms.Form):
    quiz = forms.ModelChoiceField(
        queryset=Quiz.objects.all(),
        label="Chọn Đề thi để import câu hỏi vào",
        required=True
    )
    file = forms.FileField(label="Chọn file Excel (.xlsx)")
