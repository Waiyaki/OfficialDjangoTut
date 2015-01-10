import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from polls.models import Question


class QuestionMethodTest(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions 
        with a pub_date that's in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions
        with a pub_date older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently should return True for questions
        whose pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Creates a question with the given 'question_text' published 
    the given number of days offset to now.
    Negative offset -- published in the past.
    Positive offset -- will be published in the future(yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionView(TestCase):

    def test_index_view_with_no_questions(self):
        """
        If no questions exists, an appropriate message should be
        displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(
            response.context['latest_question_list'], []
        )

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed
        in the index page.
        """
        q = create_question(question_text="Past question.", days=-30)
        q.choice_set.create(choice_text="Sure.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: Past question.>"]
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be
        displayed in the index page.
        """
        q = create_question(question_text="Future question.", days=30)
        q.choice_set.create(choice_text="Sure.")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available", status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions are present, only
        the past questions should be displayed.
        """
        q1 = create_question(question_text="Past question", days=-30)
        q2 = create_question(question_text="Future question", days=30)
        q1.choice_set.create(choice_text="Sure.")
        q2.choice_set.create(choice_text="Sure.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: Past question>"]
        )

    def test_index_view_with_two_past_questions(self):
        """
        The index view may display more than one question.
        """
        q1 = create_question(question_text="Past question 1", days=-30)
        q2 = create_question(question_text="Past question 2", days=-5)
        q1.choice_set.create(choice_text="Sure.")
        q2.choice_set.create(choice_text="Sure.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: Past question 2>", "<Question: Past question 1>"]
        )

    def test_index_view_each_returned_question_has_choice(self):
        """
        The questions displayed in the index view should only be the ones
        that have (an) associated choice(s).
        """
        with_choice = create_question(question_text="What's my choice?", days=-1)
        with_choice.choice_set.create(choice_text="Me.")

        without_choice = create_question(question_text="The buggers?", days=-1)
        response = self.client.get(reverse('polls:index'))
        for question in response.context['latest_question_list']:
            self.assertEqual(bool(question.choice_set.all()), True)



class DetailViewTest(TestCase):

    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the
        future should return a 404 not found.
        """
        future_question = create_question(question_text="Future question",
                                          days=30)
        response = self.client.get(reverse('polls:detail',
                                            args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        should display the question's text.
        """
        past_question = create_question(question_text="Past question", days=-5)
        response = self.client.get(reverse('polls:detail',
                                            args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)


class ResultsViewTest(TestCase):

    def test_results_view_with_a_future_question(self):
        """
        The results view of a question with a pub_date in the
        future should return a 404 not found.
        """
        future_question = create_question(question_text="Future question",
                                          days=30)
        response = self.client.get(reverse('polls:results',
                                            args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """
        The results view of a question with a pub_date in the past
        should display the question's text.
        """
        past_question = create_question(question_text="Past question", days=-5)
        response = self.client.get(reverse('polls:results',
                                            args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

