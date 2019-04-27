"""Primitives that manage Jenkins job of type 'Folder'"""
from pyjen.job import Job
from pyjen.utils.plugin_api import find_plugin
from pyjen.utils.helpers import create_job
from pyjen.exceptions import PluginNotSupportedError


class FolderJob(Job):
    """Jenkins job of type 'folder'"""
    def create_job(self, job_name, job_class):
        """Creates a new job on the Jenkins dashboard

        :param str job_name:
            the name for this new job
            This name should be unique, different from any other jobs currently
            managed by the Jenkins instance
        :param job_class:
            PyJen plugin class associated with the type of job to be created
        :returns: An object to manage the newly created job
        :rtype: :class:`~.job.Job`
        """
        create_job(self._api, job_name, job_class)
        retval = self.find_job(job_name)
        assert retval is not None
        return retval

    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job

        .. seealso: :py:meth:`.get_job`

        :param str job_name: the name of the job to search for
        :returns:
            If a job with the specified name can be found, and object to manage
            the job will be returned, otherwise None
        :rtype: :class:`~.job.Job`
        """
        data = self._api.get_api_data()
        tjobs = data['jobs']

        for tjob in tjobs:
            if tjob['name'] == job_name:
                return Job.instantiate(tjob, self._api)

        return None

    def clone_job(self, source_job, new_job_name, disable=True):
        """"Create a new job with the same configuration as this one

        :param source_job: job to be cloned
        :type source_job: :class:`pyjen.job.Job`
        :param str new_job_name: Name of the new job to be created
        :param bool disable:
            Indicates whether the newly created job should be disabled after
            creation to prevent builds from accidentally triggering
            immediately after creation
        :returns: reference to the newly created job
        :rtype: :class:`pyjen.job.Job`
        """
        new_job = self.create_job(new_job_name, source_job.__class__)
        new_job.config_xml = source_job.config_xml
        if disable:
            new_job.disable()
        return new_job

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def template_config_xml():
        """XML configuration template for  instantiating jobs of this type

        :returns:
            a basic XML configuration template for use when instantiating
            jobs of this type
        :rtype: :class:`str`
        """
        xml = """<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@6.7">
        <description/>
        <properties>
            <org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig plugin="pipeline-model-definition@1.3.6">
            <dockerLabel/>
            <registry plugin="docker-commons@1.13"/>
            </org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig>
        </properties>
        <folderViews class="com.cloudbees.hudson.plugins.folder.views.DefaultFolderViewHolder">
            <views>
                <hudson.model.AllView>
                    <owner class="com.cloudbees.hudson.plugins.folder.Folder" reference="../../../.."/>
                    <name>All</name>
                    <filterExecutors>false</filterExecutors>
                    <filterQueue>false</filterQueue>
                    <properties class="hudson.model.View$PropertyList"/>
                </hudson.model.AllView>
            </views>
            <tabBar class="hudson.views.DefaultViewsTabBar"/>
        </folderViews>
        <healthMetrics>
            <com.cloudbees.hudson.plugins.folder.health.WorstChildHealthMetric>
                <nonRecursive>false</nonRecursive>
            </com.cloudbees.hudson.plugins.folder.health.WorstChildHealthMetric>
        </healthMetrics>
        <icon class="com.cloudbees.hudson.plugins.folder.icons.StockFolderIcon"/>
    </com.cloudbees.hudson.plugins.folder.Folder>"""
        return xml

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "com.cloudbees.hudson.plugins.folder.Folder"


PluginClass = FolderJob


if __name__ == "__main__":  # pragma: no cover
    pass
