from django.db import models
from unidecode import unidecode
import re


class Exam(models.Model):
    title = models.CharField("Tên kỳ thi", max_length=255, unique=True)
    description = models.TextField("Mô tả", blank=True)

    class Meta:
        verbose_name = "Kỳ thi"
        verbose_name_plural = "Kỳ thi"

    def __str__(self):
        return self.title


class Quiz(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='quizzes', verbose_name="Kỳ thi")
    title = models.CharField("Tên đề thi", max_length=255)
    description = models.TextField("Mô tả", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Đề thi"
        verbose_name_plural = "Đề thi"

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="Đề thi")
    text = models.TextField("Nội dung câu hỏi")
    order = models.IntegerField("Thứ tự", default=0)
    explanation = models.TextField("Diễn giải", blank=True)

    search_acronym = models.CharField(
        max_length=500,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name="Viết tắt tìm kiếm"
    )
    search_text_normalized = models.TextField(
        blank=True,
        editable=False,
        db_index=True,
        verbose_name="Nội dung chuẩn hóa"
    )

    class Meta:
        verbose_name = "Câu hỏi"
        verbose_name_plural = "Câu hỏi"
        ordering = ['order']

    def __str__(self):
        return self.text[:100]

    def save(self, *args, **kwargs):
        self.search_acronym = _generate_acronym(self.text)
        self.search_text_normalized = unidecode(self.text.lower()) if self.text else ""
        super().save(*args, **kwargs)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name="Câu hỏi")
    text = models.TextField("Nội dung lựa chọn")
    is_correct = models.BooleanField("Là đáp án đúng", default=False)

    class Meta:
        verbose_name = "Lựa chọn"
        verbose_name_plural = "Lựa chọn"

    def __str__(self):
        return self.text[:80]


def _generate_acronym(text):
    if not text:
        return ""
    text_no_accent = unidecode(text.lower())
    words = re.findall(r'\b\w+\b', text_no_accent)
    return "".join(word[0] for word in words)
