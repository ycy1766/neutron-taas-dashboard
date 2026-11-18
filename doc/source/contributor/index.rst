..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

=================
Contributor Guide
=================

See `Horizon Contributor Documents
<https://docs.openstack.org/horizon/latest/contributor/index.html>`__
for general topics on developing a dashboard plugin for horizon.

Project layout
--------------

``neutron_taas_dashboard/api/taas.py``
    The only module that talks to Neutron. It uses
    ``openstack_dashboard.api.neutron.neutronclient`` where horizon still
    provides it and the openstacksdk ``networkclient`` otherwise.

``neutron_taas_dashboard/dashboards/project/tap_mirrors``
    Panel, table, form, views and templates.

``neutron_taas_dashboard/conf/neutron_policy.d``
    Policy rules for horizon, see :doc:`../configuration/index`.

``neutron_taas_dashboard/test``
    Unit tests, including policy tests that run the real
    ``openstack_auth`` policy engine.

Running the tests
-----------------

.. code-block:: console

   $ tox -e py3
   $ tox -e pep8
   $ tox -e docs

----

.. toctree::
   :maxdepth: 1

   DevStack plugin <devstack-plugin>
