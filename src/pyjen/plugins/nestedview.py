"""Primitives for working with Jenkins views of type 'NestedView'"""
import logging
import json
from pyjen.view import View


class NestedView(View):
    """all Jenkins related 'view' information for views of type NestedView

    Instances of this class are typically instantiated directly or indirectly
    through :py:meth:`pyjen.View.create`

    NOTE: The class associations for this type of view are confusing. When
    asking the root Jenkins API for a list of views, you'll see this:

        hudson.plugins.nested_view.NestedView

    when analysing the config.xml for the view you'll see this:

        hudson.plugins.nested__view.NestedView

    This plugin does support the "plugin" attribute in it's config.xml, so
    it has something like

        plugin="nested-view@1.17"

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :param parent:
        PyJen object that "owns" this view. Typically this is a reference to
        the :class:`pyjen.jenkins.Jenkins` object for the current Jenkins
        instance but in certain cases this may be a different object like
        a :class:`pyjen.plugins.nestedview.NestedView`.

        The parent object is expected to expose a method named `create_view`
        which can be used to clone instances of this view.
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api, parent):
        super(NestedView, self).__init__(api, parent)
        self._log = logging.getLogger(__name__)

    @property
    def views(self):
        """Gets all views contained within this view, non-recursively

        To get a recursive list of all child views and their children use
        :py:meth:`all_views`.

        :returns: list of all views contained within this view
        :rtype: :class:`list` of :class:`pyjen.view.View`
        """
        retval = list()

        data = self._api.get_api_data()

        for cur_view in data['views']:
            retval.append(View.instantiate(cur_view, self._api, self))

        return retval

    def find_view(self, view_name):
        """Attempts to locate a sub-view under this nested view by name

        NOTE: Seeing as how view names need only be unique within a single
        parent view, there may be multiple nested views with the same name.
        To reflect this requirement this method will return a list of views
        nested within this one that have the name given. If the list is empty
        then there are no matches for the given name anywhere in this
        view's sub-tree.

        :param str view_name: the name of the sub-view to locate
        :returns: List of 0 or more views with the given name
        :rtype: :class:`list` of :class:`pyjen.view.View`
        """
        retval = list()
        for cur_view in self.all_views:
            if cur_view.name == view_name:
                retval.append(cur_view)

        return retval

    @property
    def all_views(self):
        """Gets all views contained within this view, recursively

        :returns:
            list of all views contained within this view and it's children,
            recursively
        :rtype: :class:`list` of :class:`pyjen.view.View`
        """
        retval = list()
        for cur_view in self.views:

            retval.append(cur_view)

            # See if our current view is, itself a nested view. If so then
            # recurse into it appending all the views contained therein as well
            if isinstance(cur_view, NestedView):
                retval.extend(cur_view.all_views)

        return retval

    def create_view(self, view_name, view_type):
        """Creates a new sub-view within this nested view

        :param str view_name: name of the new sub-view to create
        :param str view_type: data type for newly generated view
        :returns: reference to the newly created view
        :rtype: :class:`pyjen.view.View`
        """
        view_type = view_type.replace("__", "_")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": view_name,
            "mode": view_type,
            "Submit": "OK",
            "json": json.dumps({"name": view_name, "mode": view_type})
        }

        args = {
            'data': data,
            'headers': headers
        }

        self._api.post(self._api.url + 'createView', args)
        result = self.find_view(view_name)

        # Sanity Check: views within the same parent MUST have unique names.
        # This is a hard requirement enforced by the Jenkins API. If, on the
        # other hand, our search operation yielded no results then something
        # very strange has happened (ie: a backend server problem). If the
        # post operation fails for some reason an exception will be raised and
        # this line of code should never get executed. So we do one quick
        # sanity check to make sure we have 1, and exactly 1, result from
        # our search operation.
        assert len(result) == 1

        return result[0]

    def move_view(self, existing_view):
        """Moves an existing view to a new location

        NOTE: The original view object becomes obsolete after executing this
        operation

        :param existing_view: Instance of a PyJen view to be moved
        :type existing_view: :class:`~.view.View`
        :returns: reference to new, relocated view object
        :rtype: :class:`~.view.View`
        """
        new_view = self.create_view(
            existing_view.name, existing_view.get_jenkins_plugin_name())
        new_view.config_xml = existing_view.config_xml
        existing_view.delete()
        return new_view

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.nested_view.NestedView"


PluginClass = NestedView


if __name__ == "__main__":  # pragma: no cover
    pass
