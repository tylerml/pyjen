"""Primitives for operating on job publishers of type 'Flexible Publisher'"""
from pyjen.utils.xml_plugin import XMLPlugin


class FlexiblePublisher(XMLPlugin):
    """Job plugin enabling conditional execution of post-build steps

    https://wiki.jenkins-ci.org/display/JENKINS/Flexible+Publish+Plugin
    """

    @property
    def actions(self):
        """list of publishers associated with this instance

        :returns:  list of publishers associated with this instance
        :rtype: :class:`list` of :class:`ConditionalPublisher`
        """
        nodes = self._root.find("publishers")

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Flexible publisher plugin %s not found",
                                  get_plugin_name(node))

        return retval

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "flexiblepublish"


class ConditionalPublisher(XMLPlugin):
    """a single 'conditional' publisher contained within the flexible publisher
    """

    @property
    def publisher(self):
        """action to be performed when the conditions of this publisher are met

        :returns:
            list of PyJen objects which control each conditional action to be
            performed. Return None if an publisher plugin not currently
            supported by PyJen is being used
        :rtype: :class:`list` of PyJen objects,

        """
        node = self._root.find("publisher")
        plugin = create_xml_plugin(node)

        if plugin is None:
            self._log.warning("Publisher plugin %s referenced by Flexible "
                              "Publisher not found", get_plugin_name(node))

        return plugin


PluginClass = FlexiblePublisher


if __name__ == "__main__":  # pragma: no cover
    pass
