import json
from .utils import enforce_secure_filename

from meltano.core.project import Project


class ReposHelper:
    def get_topic(self, namespace, topic_name):
        project = Project.find()
        filename = enforce_secure_filename(f"{topic_name}.topic.m5oc")
        topic = project.run_dir("models", namespace, filename)

        with topic.open() as f:
            topic = json.load(f)

        return topic
