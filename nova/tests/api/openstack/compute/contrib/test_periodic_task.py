# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

from nova.api.openstack.compute.contrib import periodic_task_on_demand
from nova.compute import api as compute_api
from nova.compute import rpcapi as compute_rpcapi
from nova import context
from nova.openstack.common import jsonutils
from nova import test
from nova.tests.api.openstack import fakes


class PeriodicTaskOnDemandTest(test.NoDBTestCase):

    def setUp(self):
        super(PeriodicTaskOnDemandTest, self).setUp()
        self.controller = periodic_task_on_demand.PeriodicTaskOnDemandController
        self.UUID = uuid.uuid4()
        self.compute_rpcapi = compute_rpcapi.ComputeAPI
        self.compute_api = compute_api.API

        self.req = fakes.HTTPRequest.blank('/v2/fake/servers/%s/action'
                                           % self.UUID)
        self.req.method = 'POST'
        self.req.body = jsonutils.dumps(
            {'periodicTaskOnDemand': {'taskName': 'task_foo'}})
        self.req.content_type = 'application/json'

        self.context = context.get_admin_context()
        self.context.user_id = 'fake'
        self.context.project_id = 'fake'
        self.context.is_admin = True

        self.flags(
            osapi_compute_extension=[
                'nova.api.openstack.compute.contrib.select_extensions'],
            osapi_compute_ext_list=['Periodic_task_on_demand'])

    def test_periodic_task_on_demand(self):
        app = fakes.wsgi_app(fake_auth_context=self.context)

        self.mox.StubOutWithMock(self.compute_rpcapi,
                                 'periodic_task_on_demand')
        self.compute_rpcapi.periodic_task_on_demand(self.context, 'task_foo')
        self.mox.ReplayAll()

        res = self.req.get_response(app)
        self.assertEqual(res.status_int, 200)

    def test_malformed_body(self):
        app = fakes.wsgi_app(fake_auth_context=self.context)
        badreq = self.req.copy()
        badreq.body = jsonutils.dumps(
            {'NonexistentMethod': {'foo': 'bar'}})

        res = badreq.get_response(app)
        self.assertEqual(res.status_int, 400)

    def test_missing_taskname(self):
        app = fakes.wsgi_app(fake_auth_context=self.context)
        badreq = self.req.copy()
        badreq.body = jsonutils.dumps(
            {'periodicTaskOnDemand': {'no-task-name': 'bar'}})

        res = badreq.get_response(app)
        self.assertEqual(res.status_int, 400)
