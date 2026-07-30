import pytest

from apps.interviews.models import Interview


@pytest.mark.django_db
def test_interview_default_status():
    interview = Interview.objects.create()

    assert interview.status == Interview.Status.IN_PROGRESS
    assert interview.user is None