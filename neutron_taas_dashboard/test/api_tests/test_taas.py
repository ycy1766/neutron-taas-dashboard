# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutronclient.v2_0 import client
from openstack_dashboard import api
from openstack_dashboard.test import helpers

from neutron_taas_dashboard.api import taas as api_taas
from neutron_taas_dashboard.test import helpers as test

neutronclient = client.Client


class TaasApiTests(test.APITestCase):

    @helpers.create_mocks({neutronclient: ('list_ext',)})
    def test_tap_mirror_list(self):
        self.mock_list_ext.return_value = {
            'tap_mirrors': self.api_tap_mirrors.list()}

        ret = api_taas.tap_mirror_list(self.request, project_id='1')

        self.assertEqual(len(self.api_tap_mirrors.list()), len(ret))
        for tm in ret:
            self.assertIsInstance(tm, api_taas.TapMirror)
        self.mock_list_ext.assert_called_once_with(
            'tap_mirrors', '/taas/tap_mirrors', retrieve_all=True,
            project_id='1')

    @helpers.create_mocks({neutronclient: ('show_ext',)})
    def test_tap_mirror_get(self):
        tm = self.api_tap_mirrors.first()
        self.mock_show_ext.return_value = {'tap_mirror': tm}

        ret = api_taas.tap_mirror_get(self.request, tm['id'])

        self.assertIsInstance(ret, api_taas.TapMirror)
        self.assertEqual(tm['id'], ret.id)
        self.assertEqual(tm['remote_port_id'], ret.remote_port_id)
        self.mock_show_ext.assert_called_once_with(
            '/taas/tap_mirrors/%s', tm['id'])

    @helpers.create_mocks({neutronclient: ('create_ext',)})
    def test_lport_mirror_create(self):
        tm = self.api_tap_mirrors.first()
        self.mock_create_ext.return_value = {'tap_mirror': tm}

        ret = api_taas.lport_mirror_create(
            self.request, name=tm['name'], description=tm['description'],
            port_id=tm['port_id'], remote_port_id=tm['remote_port_id'],
            direction=api_taas.DIRECTION_BOTH)

        self.assertIsInstance(ret, api_taas.TapMirror)
        self.mock_create_ext.assert_called_once_with(
            '/taas/tap_mirrors',
            {'tap_mirror': {'name': tm['name'],
                            'description': tm['description'],
                            'mirror_type': 'lport',
                            'port_id': tm['port_id'],
                            'remote_port_id': tm['remote_port_id'],
                            'directions': {'BOTH': None}}})

    @helpers.create_mocks({neutronclient: ('delete_ext',)})
    def test_tap_mirror_delete(self):
        tm = self.api_tap_mirrors.first()
        self.mock_delete_ext.return_value = None

        api_taas.tap_mirror_delete(self.request, tm['id'])

        self.mock_delete_ext.assert_called_once_with(
            '/taas/tap_mirrors/%s', tm['id'])

    def test_direction_of_wrapper(self):
        tm = api_taas.TapMirror({'directions': {'BOTH': None}})
        self.assertEqual(api_taas.DIRECTION_BOTH, tm.direction)
        tm = api_taas.TapMirror({'directions': {'IN': None, 'OUT': None}})
        self.assertEqual(api_taas.DIRECTION_BOTH, tm.direction)
        tm = api_taas.TapMirror({'directions': {'OUT': None}})
        self.assertEqual(api_taas.DIRECTION_OUT, tm.direction)
        tm = api_taas.TapMirror({'directions': {}})
        self.assertIsNone(tm.direction)
        self.assertEqual('-', tm.direction_display)

    @helpers.create_mocks({api.neutron: ('port_list',
                                         'network_list_for_tenant'),
                           api.nova: ('server_list',)})
    def test_mirrorable_port_choices(self):
        self.mock_port_list.return_value = self.ports.list()
        self.mock_network_list_for_tenant.return_value = \
            self.networks.list()
        self.mock_server_list.return_value = (self.servers.list(), False)

        choices = api_taas.mirrorable_port_choices(self.request)

        vm_ports = [p for p in self.ports.list()
                    if p.device_owner.startswith('compute:')]
        self.assertEqual(len(vm_ports), len(choices))
        self.assertEqual(sorted(p.id for p in vm_ports),
                         sorted(c[0] for c in choices))
        for _port_id, label in choices:
            self.assertEqual(4, len(label.split(' | ')))
        self.mock_port_list.assert_called_once_with(
            self.request, tenant_id=self.request.user.tenant_id)

    @helpers.create_mocks({api.neutron: ('is_service_enabled',)})
    def test_is_supported(self):
        self.mock_is_service_enabled.return_value = True
        self.assertTrue(api_taas.is_supported(self.request))
        self.mock_is_service_enabled.assert_called_once_with(
            self.request, config_name='enable_taas',
            ext_name='tap-mirror-lport')

    @helpers.create_mocks({api.neutron: ('is_service_enabled',)})
    def test_is_supported_on_error(self):
        self.mock_is_service_enabled.side_effect = self.exceptions.neutron
        self.assertFalse(api_taas.is_supported(self.request))
