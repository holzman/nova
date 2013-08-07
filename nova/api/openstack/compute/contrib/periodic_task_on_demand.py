## vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.




from webob import exc

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import compute
from nova.api.openstack import xmlutil
from nova.openstack.common.gettextutils import _
from nova.openstack.common import log as logging

LOG = logging.getLogger(__name__)
ALIAS = "os-periodic-task-on-demand"
authorize = extensions.extension_authorizer(
    'compute', 'periodic-task-on-demand')

class PeriodicTaskTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict('taskName'), 1)


class PeriodicTaskOnDemandController(object):
    def __init__(self, *args, **kwargs):
        self.compute_api = compute.API()

    # @wsgi.serializers(xml=PeriodicTaskTemplate)
    # def index(self, req):
    #     print 'yay index'
    #     return {'taskName': 'dingus'}

    @wsgi.serializers(xml=PeriodicTaskTemplate)
    def create(self, req, body):
        print 'fingus'
        context = req.environ['nova.context']
        authorize(context)

        print body
        try:
            entity = body['periodicTaskOnDemand']
        except (KeyError, TypeError):
            raise exc.HTTPBadRequest(_("Malformed request body"))

        try:
            task_name = entity['taskName']
        except KeyError as missing_key:
            msg = _("periodicTaskOnDemand requires %s attribute") % missing_key
            raise exc.HTTPBadRequest(explanation=msg)
        except TypeError:
            msg = _("Malformed periodicTaskOnDemand entity")
            raise exc.HTTPBadRequest(explanation=msg)
        self.compute_api.periodic_task_on_demand(context, task_name)
        return {'taskName': task_name}

class Periodic_task_on_demand(extensions.ExtensionDescriptor):
    """Enables execution of periodic tasks."""

    name = "PeriodicTaskOnDemand"
    alias = ALIAS
    namespace = ("http://docs.openstack.org/compute/ext/"
                 "periodic_task_on_demand/api/v2")
    updated = "2013-08-05T00:00:00+00:00"

    def __init__(self, ext_mgr):
        ext_mgr.register(self)

    def get_resources(self):
        resources = []
        resource = extensions.ResourceExtension(ALIAS,
                                                PeriodicTaskOnDemandController())

        resources.append(resource)
        return resources

#    def get_controller_extensions(self):
#        controller = PeriodicTaskOnDemandController()
#        extension = extensions.ControllerExtension(self, 'servers', controller)
#        return [extension]
