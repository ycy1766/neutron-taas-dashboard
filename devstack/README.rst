===========================================
DevStack plugin for neutron-taas-dashboard
===========================================

This is setup as a DevStack plugin.
For more information on DevStack plugins,
see the `DevStack Plugins documentation
<https://docs.openstack.org/devstack/latest/plugins.html>`__.

How to enable the TaaS dashboard
--------------------------------

Add the following to the localrc section of your local.conf.
You need to configure the Tap-as-a-Service DevStack plugin as well, with
the OVN driver, because the ``lport`` mirror type is implemented by the OVN
service driver. When the DevStack plugin for the TaaS dashboard is
configured, the ``neutron-taas-dashboard`` service is automatically enabled.

.. code-block:: none

   [[local|localrc]]
   enable_plugin tap-as-a-service https://opendev.org/openstack/tap-as-a-service master
   enable_plugin neutron-taas-dashboard https://github.com/ycy1766/neutron-taas-dashboard main
