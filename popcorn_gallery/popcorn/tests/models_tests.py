from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from .fixtures import (create_user, create_template, create_project,
                       create_project_category, create_external_project)
from ...attachments.tests.fixtures import create_asset
from ...attachments.models import Asset
from ..models import (Project, Template, ProjectCategory, TemplateCategory,
                      ProjectCategoryMembership)
from nose.tools import eq_, ok_


class PopcornTest(TestCase):

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_project_creation(self):
        data = {
            'author': create_user('bob'),
            'name': 'Hello World!',
            'template': create_template(),
            'metadata': '{}',
            'html': '<!DOCTYPE html>',
            }
        project = Project.objects.create(**data)
        ok_(project.id, "Project couldn't be created")
        ok_(project.uuid, "Project UUID missing")
        eq_(project.status, Project.HIDDEN)
        eq_(project.is_forkable, False)
        eq_(project.is_shared, False)
        eq_(project.is_published, False)
        eq_(project.is_external, False)
        eq_(project.views_count, 0)


    def test_external_project_creation(self):
        data = {
            'author': create_user('bob'),
            'name': 'Hello World!',
            'url': 'http://mozillapopcorn.org',
            }
        project = Project.objects.create(**data)
        ok_(project.id, "Project couldn't be created")
        ok_(project.uuid, "Project UUID missing")
        eq_(project.status, Project.HIDDEN)
        eq_(project.is_forkable, False)
        eq_(project.is_shared, False)
        eq_(project.is_published, False)
        eq_(project.is_external, True)
        eq_(project.views_count, 0)

    def test_absolute_url(self):
        project = create_project()
        url = reverse('user_project_summary', args=[project.author.username,
                                                    project.shortcode])
        eq_(project.get_absolute_url(), url)

    def test_project_url(self):
        project = create_external_project()
        url = reverse('user_project', args=[project.author.username,
                                            project.shortcode])
        eq_(project.get_project_url(), url)

    def test_edit_url(self):
        project = create_external_project()
        url = reverse('user_project_edit', args=[project.author.username,
                                                 project.shortcode])
        eq_(project.get_edit_url(), url)

    def test_project_published(self):
        project = create_project(status=Project.LIVE)
        ok_(project.is_published)

    def test_hidden_project(self):
        project = create_project(status=Project.HIDDEN)
        eq_(project.is_published, False)

    def test_removed_project(self):
        project = create_project(status=Project.REMOVED)
        eq_(project.status, project.REMOVED)
        eq_(project.is_published, False)
        eq_(project.is_removed, True)

    def test_butter_data(self):
        project = create_project()
        for attr in ['_id', 'name', 'template', 'data', 'created', 'modified']:
            ok_(attr in project.butter_data)


class TemplateTest(TestCase):

    def tearDown(self):
        Template.objects.all().delete()

    def test_template_creation(self):
        mozilla = create_user('mozilla')
        template = Template.objects.create(name='basic', slug='basic',
                                           author=mozilla)
        ok_(template.id, "Template couldn't be created")
        eq_(template.status, Template.LIVE)
        eq_(template.is_featured, False)
        eq_(template.views_count, 0)
        eq_(template.votes_count, 0)
        ok_(template.created)
        ok_(template.modified)
        eq_(len(template.asset_list), 0)
        eq_(template.template_asset, None)
        eq_(template.config_asset, None)
        eq_(template.metadata_asset, None)

    def test_template_live_manager(self):
        create_template(name='basic')
        eq_(Template.live.all().count(), 1)

    def test_template_live_manager_hidden(self):
        create_template(status=Template.HIDDEN)
        eq_(Template.live.all().count(), 0)
        eq_(Template.objects.all().count(), 1)


class ProjectCategoryTest(TestCase):

    def tearDown(self):
        ProjectCategory.objects.all().delete()

    def test_category_creation(self):
        data = {'name': 'Special'}
        category = ProjectCategory.objects.create(**data)
        ok_(category.id, 'Failed to create Category')


class TemplateCategoryTest(TestCase):

    def tearDown(self):
        TemplateCategory.objects.all().delete()

    def test_category_creation(self):
        data = {'name': 'Special'}
        category = TemplateCategory.objects.create(**data)
        ok_(category.id, 'Failed to create Category')


class ProjectCategoryMembershipTest(TestCase):

    def tearDown(self):
        for model in [ProjectCategoryMembership, ProjectCategory, User]:
            model.objects.all().delete()

    def test_membership_creation(self):
        user = create_user('bob', with_profile=True)
        data = {
            'user': user.profile,
            'project_category': create_project_category(),
            }
        membership = ProjectCategoryMembership.objects.create(**data)
        eq_(ProjectCategoryMembership.PENDING, membership.status)
        ok_(membership.created, "Missing created date")


class ProjectTemplateTests(TestCase):

    def tearDown(self):
        for model in [Asset, Template, User, Template]:
            model.objects.all().delete()

    def test_template_save_new_template(self):
        template = create_template(template_content='')
        content = '<!DOCTYPE html><html><head></head><body>HELLO WORLD</body></html>'
        create_asset(asset_content=content, template=template,
                     asset_type=Asset.TEMPLATE)
        template = Template.objects.get(id=template.id)
        template.save()
        eq_(template.template_content, content)

    def test_template_save_existing_template(self):
        content = '<!DOCTYPE html5>'
        template = create_template(template_content=content)
        create_asset(asset_content='Updated content', template=template,
                     asset_type=Asset.TEMPLATE)
        template = Template.objects.get(id=template.id)
        template.save()
        eq_(template.template_content, content)

    def test_template_save_new_config(self):
        template = create_template(config='')
        content = '{"foo": "foo"}'
        create_asset(asset_content=content, template=template,
                     asset_type=Asset.CONFIG)
        template = Template.objects.get(id=template.id)
        template.save()
        eq_(template.config, {"foo": "foo"})

    def test_template_save_existing_config(self):
        content = '{"foo": "foo"}'
        template = create_template(config=content)
        create_asset(asset_content='{"updated": "updated"}', template=template,
                     asset_type=Asset.CONFIG)
        template = Template.objects.get(id=template.id)
        template.save()
        eq_(template.config, {"foo": "foo"})

    def test_template_save_new_metadata(self):
        template = create_template(metadata='')
        content = '{"foo": "foo"}'
        create_asset(asset_content=content, template=template,
                     asset_type=Asset.DATA)
        template = Template.objects.get(id=template.id)
        template.save()
        eq_(template.metadata, content)

    def test_template_save_existing_metadata(self):
        content = '{"foo": "foo"}'
        template = create_template(metadata=content)
        create_asset(asset_content='{"updated": "updated"}', template=template,
                     asset_type=Asset.DATA)
        template = Template.objects.get(id=template.id)
        template.save()
        eq_(template.metadata, content)
