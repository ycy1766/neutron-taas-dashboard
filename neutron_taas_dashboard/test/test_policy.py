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

"""Policy checks of the panel with the real openstack_auth engine.

The Horizon test settings disable the policy check (``POLICY_CHECK_FUNCTION
= None``). These tests turn it on and load the TaaS rules shipped in
``neutron_taas_dashboard/conf/neutron_policy.d`` to prove that the rules do
what the README claims.
"""

import os

from django.test.utils import override_settings
from django.urls import reverse
from openstack_auth import policy as policy_backend
from openstack_dashboard import policy
from openstack_dashboard.test import helpers

import neutron_taas_dashboard
from neutron_taas_dashboard.api import taas as api_taas
from neutron_taas_dashboard.dashboards.project.tap_mirrors import panel
from neutron_taas_dashboard.test import helpers as test

INDEX_URL = reverse('horizon:project:tap_mirrors:index')
CREATE_URL = reverse('horizon:project:tap_mirrors:create')

POLICY_DIR = os.path.join(os.path.dirname(neutron_taas_dashboard.__file__),
                          'conf', 'neutron_policy.d')
NETWORK_POLICY = {'identity': 'keystone_policy.yaml',
                  'compute': 'nova_policy.yaml',
                  'network': 'neutron_policy.yaml'}
RULES = ('create_tap_mirror', 'get_tap_mirror', 'delete_tap_mirror')


@override_settings(POLICY_CHECK_FUNCTION='openstack_auth.policy.check',
                   POLICY_FILES=NETWORK_POLICY,
                   POLICY_DIRS={'network': [POLICY_DIR]})
class TapMirrorPolicyTests(test.TestCase):

    def setUp(self):
        super().setUp()
        policy_backend.reset()

    def tearDown(self):
        policy_backend.reset()
        super().tearDown()

    def _check(self, roles, target_project=None):
        self.setActiveUser(id=self.user.id, token=self.token,
                           username=self.user.name,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           roles=[{'name': r} for r in roles])
        target = None
        if target_project:
            target = {'project_id': target_project,
                      'tenant_id': target_project}
        return {rule: policy.check((('network', rule),), self.request,
                                   target=target)
                for rule in RULES}

    def test_rules_are_loaded(self):
        enforcer = policy_backend._get_enforcer()
        self.assertIn('network', enforcer)
        for rule in RULES:
            self.assertIn(rule, enforcer['network'].rules)

    def test_reader_can_only_view(self):
        self.assertEqual({'create_tap_mirror': False,
                          'get_tap_mirror': True,
                          'delete_tap_mirror': False},
                         self._check(['reader']))

    def test_member_own_project(self):
        self.assertEqual({'create_tap_mirror': True,
                          'get_tap_mirror': True,
                          'delete_tap_mirror': True},
                         self._check(['member']))

    def test_member_other_project(self):
        self.assertEqual({'create_tap_mirror': False,
                          'get_tap_mirror': False,
                          'delete_tap_mirror': False},
                         self._check(['member'], target_project='other'))

    def test_admin_other_project(self):
        self.assertEqual({'create_tap_mirror': True,
                          'get_tap_mirror': True,
                          'delete_tap_mirror': True},
                         self._check(['admin', 'member'],
                                     target_project='other'))

    def test_no_roles(self):
        self.assertEqual({'create_tap_mirror': False,
                          'get_tap_mirror': False,
                          'delete_tap_mirror': False},
                         self._check([]))

    def test_panel_hidden_without_get_rule(self):
        self.setActiveUser(id=self.user.id, token=self.token,
                           username=self.user.name,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           roles=[])
        self.assertFalse(panel.TapMirrors._can_access(
            panel.TapMirrors(), self.request))
        self.setActiveUser(id=self.user.id, token=self.token,
                           username=self.user.name,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           roles=[{'name': 'reader'}])
        self.assertTrue(panel.TapMirrors._can_access(
            panel.TapMirrors(), self.request))

    @override_settings(POLICY_DIRS={})
    def test_without_shipped_rules_reader_sees_buttons(self):
        """Documents why the policy file must be installed."""
        policy_backend.reset()
        self.assertEqual({'create_tap_mirror': True,
                          'get_tap_mirror': True,
                          'delete_tap_mirror': True},
                         self._check(['reader']))


@override_settings(POLICY_CHECK_FUNCTION='openstack_auth.policy.check',
                   POLICY_FILES=NETWORK_POLICY,
                   POLICY_DIRS={'network': [POLICY_DIR]})
class CreateViewPolicyTests(test.TestCase):
    """The create view refuses users without ``create_tap_mirror``."""

    def setUp(self):
        super().setUp()
        policy_backend.reset()

    def tearDown(self):
        policy_backend.reset()
        super().tearDown()

    def _login(self, roles):
        self.setActiveUser(id=self.user.id, token=self.token,
                           username=self.user.name,
                           tenant_id=self.tenant.id,
                           service_catalog=self.service_catalog,
                           roles=[{'name': r} for r in roles])

    def _form_data(self):
        tm = self.tap_mirrors.first()
        return {'name': tm.name, 'description': tm.description,
                'port_id': tm.port_id, 'remote_port_id': tm.remote_port_id,
                'direction': api_taas.DIRECTION_BOTH}

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',
                                      'lport_mirror_create')})
    def test_reader_get_is_refused(self):
        self._login(['reader'])

        res = self.client.get(CREATE_URL)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)
        self.mock_mirrorable_port_choices.assert_not_called()

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',
                                      'lport_mirror_create')})
    def test_reader_post_is_refused(self):
        self._login(['reader'])

        res = self.client.post(CREATE_URL, self._form_data())

        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)
        self.mock_lport_mirror_create.assert_not_called()

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',
                                      'lport_mirror_create')})
    def test_member_post_creates(self):
        self._login(['member'])
        tm = self.tap_mirrors.first()
        self.mock_mirrorable_port_choices.return_value = [
            (tm.port_id, 'source'), (tm.remote_port_id, 'collector')]
        self.mock_lport_mirror_create.return_value = tm

        res = self.client.post(CREATE_URL, self._form_data())

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.mock_lport_mirror_create.assert_called_once()
