from django.contrib.auth.models import User
from django.test import TestCase

from nose.tools import eq_

from ..models import Activity
from ...popcorn.models import Project, Template
from ...popcorn.tests.fixtures import (create_project, create_user,
                                       create_template)


class ActivitySignalTest(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)
        self.template = create_template()

    def tearDown(self):
        for model in [Project, Template, Activity, User]:
            model.objects.all().delete()

    def test_project_signal_created(self):
        create_project(author=self.user, template=self.template,
                       status=Project.LIVE)
        eq_(Activity.objects.get_for_user(self.user).count(), 1)

    def test_project_signal_published(self):
        project = create_project(author=self.user, template=self.template,
                                 status=Project.HIDDEN)
        eq_(Activity.objects.get_for_user(self.user).count(), 0)
        project.status = Project.LIVE
        project.save()
        eq_(Activity.objects.get_for_user(self.user).count(), 1)

    def test_project_signal_forked(self):
        alex = create_user('alex')
        original_project = create_project(author=alex, template=self.template,
                                          status=Project.LIVE)
        project = create_project(author=self.user, status=Project.LIVE,
                                 template=self.template,
                                 source=original_project)
        eq_(Activity.objects.get_for_user(self.user).count(), 1)
