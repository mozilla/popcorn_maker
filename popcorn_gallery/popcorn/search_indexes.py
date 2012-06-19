from haystack import indexes

from .models import Project, Template


class TemplateIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    def get_model(self):
        return Template

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().live.all()


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    def get_model(self):
        return Project

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().live.all()
