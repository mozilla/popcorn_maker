from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from nose.tools import eq_, ok_
from test_utils import TestCase
from voting.models import Vote
from voting.views import VOTE_DIRECTIONS

from ...popcorn.models import Template, Project
from ...popcorn.tests.fixtures import create_project, create_user


class VotingIntegrationTest(TestCase):

    def setUp(self):
        self.user = create_user('x', with_profile=True)
        self.project = create_project(status=Project.LIVE)

    def tearDown(self):
        for model in [Template, Project,Vote, User]:
            model.objects.all().delete()

    def add_vote(self, project, user, direction):
        vote = dict(VOTE_DIRECTIONS)[direction]
        return Vote.objects.record_vote(project, user, vote)

    def assertRedirectsLogin(self, response):
        self.assertRedirects(response, reverse('login'))

    def assertRedirects(self, response, url):
        eq_(response.status_code, 302)
        url = 'http://testserver%s' % url
        ok_(url in response['Location'])

    def get_project_url(self, direction):
        return reverse('vote', args=['project', self.project.pk, direction])

    def test_anon_voting_get(self):
        url = self.get_project_url('up')
        response = self.client.get(url)
        eq_(response.status_code, 404)

    def test_anon_voting_post(self):
        url = self.get_project_url('up')
        response = self.client.post(url, {})
        self.assertRedirectsLogin(response)

    def test_vote_user_get(self):
        self.client.login(username='x', password='x')
        response = self.client.get(self.get_project_url('up'))
        eq_(response.status_code, 404)
        self.client.logout()

    def test_vote_user_post(self):
        self.client.login(username='x', password='x')
        response = self.client.post(self.get_project_url('up'), {})
        self.assertRedirects(response, self.project.get_absolute_url())
        ok_(Vote.objects.get_for_user(self.project, self.user))
        score = Vote.objects.get_score(self.project)
        eq_(score['score'], 1)
        eq_(score['num_votes'], 1)

    def test_vote_clear_get_anon(self):
        self.add_vote(self.project, self.user, 'up')
        response = self.client.get(self.get_project_url('clear'))
        eq_(response.status_code, 404)

    def test_vote_clear_post_anon(self):
        self.add_vote(self.project, self.user, 'up')
        response = self.client.post(self.get_project_url('clear'), {})
        self.assertRedirectsLogin(response)

    def test_vote_clear_get(self):
        self.client.login(username='x', password='x')
        self.add_vote(self.project, self.user, 'up')
        response = self.client.get(self.get_project_url('clear'))
        eq_(response.status_code, 404)
        self.client.logout()

    def test_vote_clear_post(self):
        self.client.login(username='x', password='x')
        self.add_vote(self.project, self.user, 'up')
        response = self.client.post(self.get_project_url('clear'), {})
        self.assertRedirects(response, self.project.get_absolute_url())
        score = Vote.objects.get_score(self.project)
        eq_(score['score'], 0)
        eq_(score['num_votes'], 0)
        self.client.logout()

    def test_double_vote(self):
        self.client.login(username='x', password='x')
        self.add_vote(self.project, self.user, 'up')
        response = self.client.post(self.get_project_url('up'), {})
        self.assertRedirects(response, self.project.get_absolute_url())
        ok_(Vote.objects.get_for_user(self.project, self.user))
        score = Vote.objects.get_score(self.project)
        eq_(score['score'], 1)
        eq_(score['num_votes'], 1)

    def test_double_clear(self):
        self.client.login(username='x', password='x')
        self.add_vote(self.project, self.user, 'up')
        self.add_vote(self.project, self.user, 'clear')
        response = self.client.post(self.get_project_url('clear'), {})
        self.assertRedirects(response, self.project.get_absolute_url())
        score = Vote.objects.get_score(self.project)
        eq_(score['score'], 0)
        eq_(score['num_votes'], 0)
        self.client.logout()

    def test_clear_unexistent(self):
        self.client.login(username='x', password='x')
        other = create_user('y')
        self.add_vote(self.project, other, 'up')
        response = self.client.post(self.get_project_url('clear'), {})
        self.assertRedirects(response, self.project.get_absolute_url())
        score = Vote.objects.get_score(self.project)
        eq_(score['score'], 1)
        eq_(score['num_votes'], 1)
        self.client.logout()
