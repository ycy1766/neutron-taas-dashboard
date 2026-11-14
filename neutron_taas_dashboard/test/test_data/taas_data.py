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

from openstack_dashboard.test.test_data import utils

from neutron_taas_dashboard.api import taas


def data(TEST):
    # Wrapped objects as returned by neutron_taas_dashboard.api.taas.
    TEST.tap_mirrors = utils.TestDataContainer()
    # Raw dicts as returned by neutronclient.
    TEST.api_tap_mirrors = utils.TestDataContainer()

    vm_ports = [p for p in TEST.ports.list()
                if p.device_owner.startswith('compute:')]
    source_port = vm_ports[0]
    collector_port = vm_ports[1]

    tap_mirror_dict = {
        'id': '5b4bd5b0-1f22-4d4d-9c5e-7a6d9a6a0001',
        'tenant_id': '1',
        'project_id': '1',
        'name': 'web-to-ids',
        'description': 'copy web traffic to the IDS',
        'mirror_type': taas.MIRROR_TYPE_LPORT,
        'port_id': source_port.id,
        'remote_port_id': collector_port.id,
        'remote_ip': None,
        'directions': {'BOTH': None},
    }
    TEST.api_tap_mirrors.add(tap_mirror_dict)
    TEST.tap_mirrors.add(taas.TapMirror(tap_mirror_dict))

    tap_mirror_dict = {
        'id': '5b4bd5b0-1f22-4d4d-9c5e-7a6d9a6a0002',
        'tenant_id': '1',
        'project_id': '1',
        'name': '',
        'description': '',
        'mirror_type': taas.MIRROR_TYPE_LPORT,
        'port_id': collector_port.id,
        'remote_port_id': source_port.id,
        'remote_ip': None,
        'directions': {'IN': None},
    }
    TEST.api_tap_mirrors.add(tap_mirror_dict)
    TEST.tap_mirrors.add(taas.TapMirror(tap_mirror_dict))
