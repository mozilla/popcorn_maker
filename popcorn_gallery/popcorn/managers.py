from django.db import models


class ProjectManager(models.Manager):

    def get_query_set(self):
        return (super(ProjectManager, self).get_query_set()
                .filter(status=self.model.LIVE))
