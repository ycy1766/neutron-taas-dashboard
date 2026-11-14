==================
neutron-taas-dashboard
==================

Horizon plugin that adds a **Project > Network > Tap Mirrors** panel for the
Tap-as-a-Service ``tap_mirrors`` API.

First version (this scaffold)
-----------------------------

* ``lport`` tap mirrors only: copy the traffic of one VM port to another VM
  port of the same project (``tap-mirror-lport`` extension).
* List, create, show and delete. Source port, collector port and direction
  can not be changed after creation (only name and description can), so the
  first version has no edit form: delete and create again.
* No status column. The API reports that the mirror was recorded, not that
  the backend is forwarding packets.
* Only ``compute:*`` ports are offered as source and collector. This is a
  deliberate UI restriction of the first version, not a server rule.
* Port labels show the server name. Nova returns at most ``osapi_max_limit``
  servers (1000 by default) for the one list call made here, so in a larger
  project some ports are labelled with the server id instead. Port selection
  itself is not affected.
* All Neutron calls live in ``neutron_taas_dashboard/api/taas.py`` and use the
  generic ``python-neutronclient`` HTTP methods, because Horizon 2025.1 still
  builds that client and openstacksdk 4.4.1 does not know ``remote_port_id``
  as a first-class attribute. Switching to ``api.neutron.networkclient``
  later touches this module only.

Enable
------

Install the package into the Horizon virtualenv and copy (or link)
``neutron_taas_dashboard/enabled/_7200_project_tap_mirrors_panel.py`` to
``openstack_dashboard/local/enabled/``. With the openstack-helm Horizon
chart this happens automatically when ``neutron_taas_dashboard`` is listed
in ``conf.horizon.extra_panels`` (it is in the chart defaults).

The panel is shown when Neutron advertises the ``tap-mirror-lport``
extension and ``OPENSTACK_NEUTRON_NETWORK['enable_taas']`` is not
``False``. That only decides visibility. Whether the user may create or
delete is decided by the Neutron policy on the server, and Horizon hides the
buttons by its own copy of that policy: point ``POLICY_DIRS['network']`` at
``neutron_taas_dashboard/conf/neutron_policy.d`` (or merge its rules into the
chart's ``conf.horizon.policy.network``), otherwise the buttons
are shown to every project member and reader (Horizon falls back to its
``default`` rule) and a reader gets an error from the server instead.

Tests
-----

::

    tox -e py3
    tox -e pep8
