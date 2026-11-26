from django.db import migrations, models


def _dup_key(normalized):
    return " ".join((normalized or "").split())


def forwards(apps, schema_editor):
    """Chuyển FK quiz -> M2M quizzes và gộp câu hỏi trùng (giữ bản mới nhất)."""
    Question = apps.get_model('quiz', 'Question')
    Through = Question.quizzes_new.through

    groups = {}
    for q_id, quiz_id, normalized in Question.objects.values_list('id', 'quiz_id', 'search_text_normalized'):
        groups.setdefault(_dup_key(normalized), []).append((q_id, quiz_id))

    # Mỗi nhóm trùng giữ câu mới nhất (id lớn nhất), gắn với mọi đề của cả nhóm.
    # Dùng set để không sinh cặp (câu hỏi, đề) trùng khi câu bị import 2 lần vào cùng 1 đề.
    pairs, old_ids = set(), []
    for items in groups.values():
        keep_id = max(q_id for q_id, _ in items)
        pairs.update((keep_id, quiz_id) for _, quiz_id in items)
        old_ids += [q_id for q_id, _ in items if q_id != keep_id]

    Through.objects.bulk_create([Through(question_id=q_id, quiz_id=quiz_id) for q_id, quiz_id in pairs])
    for i in range(0, len(old_ids), 500):
        Question.objects.filter(pk__in=old_ids[i:i + 500]).delete()


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
