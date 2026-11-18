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

============
Installation
============

Requirements
------------

* Horizon 2025.1 (Epoxy) or later, in the same Python environment as the
  plugin. The plugin uses ``python-neutronclient`` through Horizon on
  releases that still ship it and the ``openstacksdk`` based network
  client on later releases.
* Neutron with the Tap-as-a-Service plugin and its OVN service driver,
  advertising the ``tap-mirror-lport`` extension. Without that extension
  the panel is hidden.

Manual Installation
-------------------

Before installing neutron-taas-dashboard,
you first need to install horizon in your environment.

Fetch the source code from git and run pip install.
Make sure to install neutron-taas-dashboard into the same python environment
where horizon is installed.

.. code-block:: console

   $ git clone https://github.com/ycy1766/neutron-taas-dashboard
   $ cd neutron-taas-dashboard
   $ sudo pip install .

Enable the horizon plugin.

.. code-block:: console

   $ cp neutron_taas_dashboard/enabled/_7200_project_tap_mirrors_panel.py \
         /opt/stack/horizon/openstack_dashboard/local/enabled/_7200_project_tap_mirrors_panel.py

.. note::

   The directory ``local/enabled`` may be different depending on your
   environment or distribution used. For example, for Ubuntu, this is
   ``/usr/share/openstack-dashboard/openstack_dashboard/local/enabled``.
   With the openstack-helm Horizon chart the file is linked automatically
   when ``neutron_taas_dashboard`` is listed in
   ``conf.horizon.extra_panels``.

.. note::

   The number of the plugin enabled file determines the order of panels.
   If you would like to configure the place of the Tap Mirrors panel,
   change the number of the file.

.. note::

   For more detail of the horizon plugin settings,
   see `Pluggable Settings
   <https://docs.openstack.org/horizon/latest/configuration/pluggable_panels.html>`__
   in the horizon documentation.

Install the policy rules, see :doc:`../configuration/index`.

Compile the message catalogs of the Neutron TaaS dashboard (only needed
once translations are shipped).

.. code-block:: console

   $ cd neutron-taas-dashboard
   $ ./manage.py compilemessages

Run the Django update commands (if you use).

.. code-block:: console

   $ DJANGO_SETTINGS_MODULE=openstack_dashboard.settings python manage.py collectstatic --noinput
   $ DJANGO_SETTINGS_MODULE=openstack_dashboard.settings python manage.py compress --force

Restart Apache:

.. code-block:: console

   $ sudo service apache2 restart
