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
from nova.api.openstack import xmlutil
from nova import compute
from nova.openstack.common.gettextutils import _
from nova.openstack.common import log as logging

LOG = logging.getLogger(__name__)
ALIAS = "os-periodic-task-on-demand"
authorize = extensions.extension_authorizer('compute', 'v3:' + ALIAS)


class PeriodicTaskTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('periodicTaskOnDemand',
                                       selector='periodicTaskOnDemand')
        root.set('taskName')
        return xmlutil.MasterTemplate(root, 1)


class PeriodicTaskOnDemandController(object):
    def __init__(self, *args, **kwargs):
        self.compute_api = compute.API()

    @wsgi.serializers(xml=PeriodicTaskTemplate)
    def create(self, req, body):
        print 'yoooo'
        context = req.environ['nova.context']
        authorize(context)

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
        return body


class PeriodicTaskOnDemand(extensions.V3APIExtensionBase):
    """Enables execution of periodic tasks."""

    name = "PeriodicTaskOnDemand"
    alias = ALIAS
    namespace = "http://docs.openstack.org/compute/ext/%s/api/v3" % ALIAS
    version = 1

    def get_resources(self):
        resources = []
        resource = extensions.ResourceExtension(
            ALIAS, PeriodicTaskOnDemandController())
        resources.append(resource)
        return resources

    def get_controller_extensions(self):
        return []
