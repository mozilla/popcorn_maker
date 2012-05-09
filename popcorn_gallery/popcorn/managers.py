from django.db import models


class ProjectManager(models.Manager):

    def get_query_set(self):
        return (super(ProjectManager, self).get_query_set()
                .filter(status=self.model.LIVE, is_shared=True,
                        is_removed=False))


class TemplateManager(models.Manager):

    def get_query_set(self):
        return (super(TemplateManager, self).get_query_set()
                .filter(status=self.model.LIVE))
