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

from django.urls import reverse
from openstack_dashboard.test import helpers

from neutron_taas_dashboard.api import taas as api_taas
from neutron_taas_dashboard.test import helpers as test


INDEX_URL = reverse('horizon:project:tap_mirrors:index')
CREATE_URL = reverse('horizon:project:tap_mirrors:create')


class TapMirrorViewTests(test.TestCase):

    def _port_labels(self):
        return {p.id: 'label of %s' % p.id for p in self.ports.list()}

    @helpers.create_mocks({api_taas: ('tap_mirror_list', 'project_ports')})
    def test_index(self):
        self.mock_tap_mirror_list.return_value = self.tap_mirrors.list()
        self.mock_project_ports.return_value = self._port_labels()

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'project/tap_mirrors/index.html')
        rows = res.context['table'].data
        self.assertEqual(len(self.tap_mirrors.list()), len(rows))
        first = self.tap_mirrors.first()
        self.assertEqual('label of %s' % first.port_id, rows[0].port_display)
        self.assertEqual('label of %s' % first.remote_port_id,
                         rows[0].remote_port_display)
        self.mock_tap_mirror_list.assert_called_once_with(
            helpers.IsHttpRequest(), project_id=self.tenant.id,
            mirror_type='lport')

    @helpers.create_mocks({api_taas: ('tap_mirror_list',)})
    def test_index_api_error(self):
        self.mock_tap_mirror_list.side_effect = self.exceptions.neutron

        res = self.client.get(INDEX_URL)

        self.assertTemplateUsed(res, 'project/tap_mirrors/index.html')
        self.assertEqual(0, len(res.context['table'].data))
        self.assertMessageCount(res, error=1)

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',)})
    def test_create_get(self):
        self.mock_mirrorable_port_choices.return_value = [
            (p.id, 'label of %s' % p.id) for p in self.ports.list()[:2]]

        res = self.client.get(CREATE_URL)

        self.assertTemplateUsed(res, 'project/tap_mirrors/create.html')
        self.assertNoFormErrors(res)

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',
                                      'lport_mirror_create')})
    def test_create_post(self):
        tm = self.tap_mirrors.first()
        self.mock_mirrorable_port_choices.return_value = [
            (tm.port_id, 'source'), (tm.remote_port_id, 'collector')]
        self.mock_lport_mirror_create.return_value = tm
        form_data = {'name': tm.name,
                     'description': tm.description,
                     'port_id': tm.port_id,
                     'remote_port_id': tm.remote_port_id,
                     'direction': api_taas.DIRECTION_BOTH}

        res = self.client.post(CREATE_URL, form_data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.mock_lport_mirror_create.assert_called_once_with(
            helpers.IsHttpRequest(),
            name=tm.name, description=tm.description,
            port_id=tm.port_id, remote_port_id=tm.remote_port_id,
            direction=api_taas.DIRECTION_BOTH)

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',
                                      'lport_mirror_create')})
    def test_create_post_same_port_rejected(self):
        tm = self.tap_mirrors.first()
        self.mock_mirrorable_port_choices.return_value = [
            (tm.port_id, 'source'), (tm.remote_port_id, 'collector')]
        form_data = {'name': tm.name,
                     'description': tm.description,
                     'port_id': tm.port_id,
                     'remote_port_id': tm.port_id,
                     'direction': api_taas.DIRECTION_IN}

        res = self.client.post(CREATE_URL, form_data)

        self.assertFormErrors(res, 1)
        self.mock_lport_mirror_create.assert_not_called()

    @helpers.create_mocks({api_taas: ('mirrorable_port_choices',
                                      'lport_mirror_create')})
    def test_create_post_api_error(self):
        tm = self.tap_mirrors.first()
        self.mock_mirrorable_port_choices.return_value = [
            (tm.port_id, 'source'), (tm.remote_port_id, 'collector')]
        self.mock_lport_mirror_create.side_effect = self.exceptions.neutron
        form_data = {'name': tm.name,
                     'description': tm.description,
                     'port_id': tm.port_id,
                     'remote_port_id': tm.remote_port_id,
                     'direction': api_taas.DIRECTION_OUT}

        res = self.client.post(CREATE_URL, form_data)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)

    @helpers.create_mocks({api_taas: ('tap_mirror_get', 'project_ports')})
    def test_detail(self):
        tm = self.tap_mirrors.first()
        self.mock_tap_mirror_get.return_value = tm
        self.mock_project_ports.return_value = self._port_labels()

        res = self.client.get(
            reverse('horizon:project:tap_mirrors:detail', args=[tm.id]))

        self.assertTemplateUsed(res, 'horizon/common/_detail.html')
        self.assertTemplateUsed(
            res, 'project/tap_mirrors/_detail_overview.html')
        self.assertEqual(tm.id, res.context['tap_mirror'].id)
        self.assertContains(res, 'label of %s' % tm.remote_port_id)
        self.mock_tap_mirror_get.assert_called_once_with(
            helpers.IsHttpRequest(), tm.id)

    @helpers.create_mocks({api_taas: ('tap_mirror_list', 'project_ports',
                                      'tap_mirror_delete')})
    def test_delete(self):
        tm = self.tap_mirrors.first()
        self.mock_tap_mirror_list.return_value = self.tap_mirrors.list()
        self.mock_project_ports.return_value = self._port_labels()
        self.mock_tap_mirror_delete.return_value = None
        form_data = {'action': 'tap_mirrors__delete__%s' % tm.id}

        res = self.client.post(INDEX_URL, form_data)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.mock_tap_mirror_delete.assert_called_once_with(
            helpers.IsHttpRequest(), tm.id)

    @helpers.create_mocks({api_taas: ('tap_mirror_list', 'project_ports',
                                      'tap_mirror_delete')})
    def test_delete_api_error_is_reported(self):
        tm = self.tap_mirrors.first()
        self.mock_tap_mirror_list.return_value = self.tap_mirrors.list()
        self.mock_project_ports.return_value = self._port_labels()
        self.mock_tap_mirror_delete.side_effect = self.exceptions.neutron
        form_data = {'action': 'tap_mirrors__delete__%s' % tm.id}

        res = self.client.post(INDEX_URL, form_data)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1, success=0)
        self.mock_tap_mirror_delete.assert_called_once_with(
            helpers.IsHttpRequest(), tm.id)

    @helpers.create_mocks({api_taas: ('tap_mirror_list', 'project_ports',
                                      'tap_mirror_delete')})
    def test_delete_partial_failure(self):
        mirrors = self.tap_mirrors.list()
        self.mock_tap_mirror_list.return_value = mirrors
        self.mock_project_ports.return_value = self._port_labels()
        self.mock_tap_mirror_delete.side_effect = [None,
                                                   self.exceptions.neutron]
        form_data = {'action': 'tap_mirrors__delete',
                     'object_ids': [tm.id for tm in mirrors]}

        res = self.client.post(INDEX_URL, form_data)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        # Horizon reports the failed rows as an error and downgrades the
        # message about the deleted rows to "info".
        self.assertMessageCount(info=1, error=1, success=0)
        self.assertEqual(2, self.mock_tap_mirror_delete.call_count)

    @helpers.create_mocks({api_taas: ('tap_mirror_get',)})
    def test_detail_not_found(self):
        self.mock_tap_mirror_get.side_effect = self.exceptions.neutron

        res = self.client.get(
            reverse('horizon:project:tap_mirrors:detail', args=['missing']))

        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertMessageCount(error=1)

    @helpers.create_mocks({api_taas: ('tap_mirror_get', 'project_ports')})
    def test_detail_non_lport_has_no_delete(self):
        tm = api_taas.TapMirror(dict(self.api_tap_mirrors.first(),
                                     mirror_type='gre', remote_port_id=None,
                                     remote_ip='192.0.2.10'))
        self.mock_tap_mirror_get.return_value = tm
        self.mock_project_ports.return_value = self._port_labels()

        res = self.client.get(
            reverse('horizon:project:tap_mirrors:detail', args=[tm.id]))

        self.assertEqual(200, res.status_code)
        self.assertNotContains(res, 'tap_mirrors__delete')
        self.assertContains(res, '192.0.2.10')
