from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views import generic

from polls.models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return a list of the last five published questions.
        Only return a question if it has an associated answer.
        """
        questions = Question.objects.filter(pub_date__lte=timezone.now()
            ).order_by('-pub_date')[:5]
        return [question for question in questions if question.choice_set.all()]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Exclude results of unpublished questions.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "You didn't select a choice.",
            })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return a HttpResponseRedirect after successfully processing POST
        # data. Prevents data from being processed twice if user hits
        # back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))