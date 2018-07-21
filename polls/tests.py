import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    """
    Create a question with the given 'question_text' and published the
    number of 'days' offset to now (negative for questions published in
    the past, positive for questions that have yet to be published.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

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

class QuestionViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        create_question('Past question.', -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future are not displayed on the index
        page.
        """
        create_question('Future question.', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        If both past and future questions exist, only past questions are
        displayed.
        """
        create_question('Past question.', -30)
        create_question('Future question.', 5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions in correct
        order.
        """
        create_question('Past question 2.', days=-5)
        create_question('Past question 1.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a future question returns a 404 not found.
        """
        future_question = create_question('Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a past question displays the questions text.
        """
        past_question = create_question('Past question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
