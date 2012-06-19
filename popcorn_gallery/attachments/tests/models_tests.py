from os.path import abspath, join, dirname

from django.test import TestCase
from django.core.files import File
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from .fixtures import create_asset, create_template
from ..models import Asset
from ...popcorn.models import Template
from ...popcorn.storage import TemplateStorage
from nose.tools import eq_, ok_


class AssetTest(TestCase):

    def setUp(self):
        self.template = create_template()
        self.storage = TemplateStorage()

    def tearDown(self):
        for model in [Asset, Template, User]:
            model.objects.all().delete()

    def get_asset_file(self):
        asset_file = ContentFile('<DOCTYPE !html5>')
        asset_file.name = 'index.html'
        return asset_file

    def test_asset_creation(self):
        data = {
            'asset': self.get_asset_file(),
            'template': self.template,
            }
        asset = Asset.objects.create(**data)
        ok_(asset.id)
        ok_(self.storage.exists(asset.asset.name))
        eq_(len(self.template.asset_list), 1)

    def test_asset_removal(self):
        asset = create_asset(template=self.template)
        asset.delete()
        eq_(self.storage.exists(asset.asset.name), False)

    def test_asset_template(self):
        create_asset(template=self.template, asset_type=Asset.TEMPLATE)
        eq_(len(self.template.asset_list), 1)
        ok_(self.template.template_asset)

    def test_asset_config(self):
        create_asset(template=self.template, asset_type=Asset.CONFIG)
        eq_(len(self.template.asset_list), 1)
        ok_(self.template.config_asset)

    def test_asset_metadata(self):
        create_asset(template=self.template, asset_type=Asset.DATA)
        eq_(len(self.template.asset_list), 1)
        ok_(self.template.metadata_asset)
