from django.db import migrations, models


def _dup_key(normalized):
    return " ".join((normalized or "").split())


def forwards(apps, schema_editor):
    """Chuyển FK quiz -> M2M quizzes và gộp câu hỏi trùng (giữ bản mới nhất)."""
    Question = apps.get_model('quiz', 'Question')
    Through = Question.quizzes_new.through

    Through.objects.bulk_create([
        Through(question_id=q_id, quiz_id=quiz_id)
        for q_id, quiz_id in Question.objects.values_list('id', 'quiz_id')
    ])

    groups = {}
    for q_id, normalized in Question.objects.values_list('id', 'search_text_normalized'):
        groups.setdefault(_dup_key(normalized), []).append(q_id)

    for ids in groups.values():
        if len(ids) < 2:
            continue
        ids.sort()
        keep_id, old_ids = ids[-1], ids[:-1]
        keep = Question.objects.get(pk=keep_id)
        quiz_ids = set(Through.objects.filter(question_id__in=old_ids).values_list('quiz_id', flat=True))
        keep.quizzes_new.add(*quiz_ids)
        Question.objects.filter(pk__in=old_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_add_choice_search_normalized'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='quizzes_new',
            field=models.ManyToManyField(related_name='+', to='quiz.quiz', verbose_name='Đề thi'),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='question',
            name='quiz',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='quizzes_new',
            new_name='quizzes',
        ),
        migrations.AlterField(
            model_name='question',
            name='quizzes',
            field=models.ManyToManyField(related_name='questions', to='quiz.quiz', verbose_name='Đề thi'),
        ),
    ]
