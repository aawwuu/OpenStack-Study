
from keystoneauth1 import loading
from keystoneauth1 import session
from cinderclient import client as cinder_client

loader = loading.get_plugin_loader('password')
auth=loader.load_from_options(\
                auth_url="http://controller:35357/v3",
                username="admin",
                password="ADMIN_PASS",
                project_name="admin",
                user_domain_name="default",
                project_domain_name="default")
sess=session.Session(auth=auth)
ct = cinder_client.Client("2", session=sess)
print ct.volumes.list()

