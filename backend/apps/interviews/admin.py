from django.contrib import admin

from apps.interviews.models import Answer, Interview, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    show_change_link = True


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status",)
    inlines = [QuestionInline]


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "interview", "text", "created_at")
    inlines = [AnswerInline]
