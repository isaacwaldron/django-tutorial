import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question

class QuestionModelTests(TestCase):
    def run_was_published_recently_test(self, timeDelta, expected):
        time = timezone.now() + timeDelta
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), expected)

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        self.run_was_published_recently_test(datetime.timedelta(days=30), False)

    def test_was_published_recntly_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is less than one day old.
        """
        self.run_was_published_recently_test(datetime.timedelta(days=-1, seconds=1), True)

    def test_was_published_recntly_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is more than one day old.
        """
        self.run_was_published_recently_test(datetime.timedelta(days=-1, seconds=-1), False)
