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

=============
Configuration
=============

Panel visibility
----------------

The Tap Mirrors panel is displayed when the Neutron server advertises the
``tap-mirror-lport`` extension. It can be hidden regardless of the server
with the ``enable_taas`` key of ``OPENSTACK_NEUTRON_NETWORK`` in the
horizon ``local_settings.py``:

.. code-block:: python

   OPENSTACK_NEUTRON_NETWORK = {
       # ...
       'enable_taas': False,
   }

Policy rules
------------

Horizon decides which buttons to show with its own copy of the Neutron
policy. The default Neutron policy file shipped with horizon has no
Tap-as-a-Service rules, so without additional configuration every TaaS
rule falls back to the ``default`` rule (``admin_or_owner``) and a project
reader sees Create and Delete buttons that the Neutron server will reject.

The plugin ships the rules in
``neutron_taas_dashboard/conf/neutron_policy.d/taas.yaml``. Point
``POLICY_DIRS`` at that directory (an absolute path works, a relative one is
joined to ``POLICY_FILES_PATH``):

.. code-block:: python

   POLICY_DIRS = {
       'network': ['/opt/stack/neutron-taas-dashboard/neutron_taas_dashboard/conf/neutron_policy.d'],
   }

The check strings mirror ``neutron_taas/policies/tap_mirror.py``:

.. literalinclude:: ../../../neutron_taas_dashboard/conf/neutron_policy.d/taas.yaml
   :language: yaml
   :start-after: # The check strings

The Neutron server remains the authority: the rules above only control what
horizon shows, every request is still checked by the server policy.

For more configurations, see
`Configuration Guide
<https://docs.openstack.org/horizon/latest/configuration/index.html>`__
in the Horizon documentation.
