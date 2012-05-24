from django.contrib.auth.models import User
from django.test import TestCase

from nose.tools import eq_
from .fixtures import create_user, create_project
from ..models import Project, Template



class ProjectsManagerTest(TestCase):

    def setUp(self):
        self.user = create_user('bob')

    def tearDown(self):
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def test_project_live_manager(self):
        create_project(status=Project.LIVE, is_shared=True, author=self.user)
        self.assertEqual(Project.live.all().count(), 1)

    def test_project_live_manager_hidden(self):
        create_project(status=Project.HIDDEN, author=self.user)
        self.assertEqual(Project.live.all().count(), 0)
        self.assertEqual(Project.objects.all().count(), 1)

    def test_project_live_manager_removed(self):
        create_project(status=Project.LIVE, is_removed=True, is_shared=True,
                       author=self.user)
        self.assertEqual(Project.live.all().count(), 0)
        self.assertEqual(Project.objects.all().count(), 1)

    def test_project_live_manager_not_shared(self):
        create_project(status=Project.LIVE, is_shared=False, author=self.user)
        self.assertEqual(Project.live.all().count(), 0)
        self.assertEqual(Project.objects.all().count(), 1)

    def test_project_user_fork(self):
        project_original = create_project(status=Project.LIVE, is_shared=False,
                                 author=self.user)
        alex = create_user('alex')
        project = Project.objects.fork(project_original, alex)
        self.assertFalse(project_original.id == project.id)
        eq_(project.author, alex)
        for attr in ['name', 'description', 'template', 'metadata', 'html']:
            eq_(getattr(project, attr), getattr(project_original, attr))
        eq_(project.source, project_original)
        eq_(project.status, Project.LIVE)

    def test_project_own_fork(self):
        project_original = create_project(status=Project.LIVE, is_shared=False,
                                          author=self.user)
        project = Project.objects.fork(project_original, self.user)
        self.assertFalse(project_original.id == project.id)
        eq_(project.author, self.user)
        for attr in ['name', 'description', 'template', 'metadata', 'html',
                     'status']:
            eq_(getattr(project, attr), getattr(project_original, attr))

    def test_projects_for_user(self):
        create_project(status=Project.HIDDEN, is_shared=False, author=self.user)
        eq_(Project.objects.get_for_user(self.user).count(), 1)

    def test_projects_for_user_removed(self):
        create_project(status=Project.LIVE, is_shared=True, author=self.user,
                       is_removed=True)
        eq_(Project.objects.get_for_user(self.user).count(), 0)
