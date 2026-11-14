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
from openstack_auth import policy as policy_backend
from openstack_dashboard import policy

import neutron_taas_dashboard
from neutron_taas_dashboard.dashboards.project.tap_mirrors import panel
from neutron_taas_dashboard.test import helpers as test

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
