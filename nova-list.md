# nova list 代码分析

```shell
# nova --debug list
DEBUG (session:375) REQ: curl -g -i -X GET http://10.131.73.105:10006/v3 -H "Accept: application/json" -H "User-Agent: nova keystoneauth1/3.1.0 python-requests/2.11.1 CPython/2.7.5"
REQ: curl -g -i -X GET http://10.131.73.105:10010/v2.1 -H "User-Agent: python-novaclient" -H "Accept: application/json" -H "X-Auth-Token: {SHA1}89227ac26d043c57ac8879a83e53c0992e3e824e"
DEBUG (session:375) REQ: curl -g -i -X GET http://10.131.73.105:10010/v2.1 -H "User-Agent: python-novaclient" -H "Accept: application/json" -H "X-Auth-Token: {SHA1}89227ac26d043c57ac8879a83e53c0992e3e824e"
DEBUG (session:375) REQ: curl -g -i -X GET http://10.131.73.105:10010/v2.1/servers/detail -H "OpenStack-API-Version: compute 2.53" -H "User-Agent: python-novaclient" -H "Accept: application/json" -H "X-OpenStack-Nova-API-Version: 2.53" -H "X-Auth-Token: {SHA1}89227ac26d043c57ac8879a83e53c0992e3e824e"
```

其中

`bind 10.131.73.105:10006	keystone-admin`

`bind 10.131.73.105:10010	nova-api`



nova 命令位于 `/usr/bin/nova`

```python
# cat /usr/bin/nova

#!/usr/bin/python2
# PBR Generated from u'console_scripts'

import sys

from novaclient.shell import main


if __name__ == "__main__":
    sys.exit(main())
```

看 `/usr/lib/python2.7/site-packages/novaclient/shell.py`

```python
def main():
    try:
        argv = [encodeutils.safe_decode(a) for a in sys.argv[1:]]
        OpenStackComputeShell().main(argv)
    except Exception as exc:
        logger.debug(exc, exc_info=1)
        if six.PY2:
            message = encodeutils.safe_encode(six.text_type(exc))
        else:
            message = encodeutils.exception_to_unicode(exc)
        print("ERROR (%(type)s): %(msg)s" % {
              'type': exc.__class__.__name__,
              'msg': message},
              file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(_("... terminating nova client"), file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()

```

调用  `OpenStackComputeShell().main(argv)`

找到类 `OpenStackComputeShell`， 查看 `main` 方法

`novaclient/shell.py`

```python
class OpenStackComputeShell(object):
……
     def main(self, argv):
         # Parse args once to find version and debug settings
         parser = self.get_base_parser(argv)
         (args, args_list) = parser.parse_known_args(argv)
 
         self.setup_debugging(args.debug)
         self.extensions = []
         do_help = args.help or not args_list or args_list[0] == 'help'
 		…… 
         # FIXME(usrleon): Here should be restrict for project id same as
         # for os_username or os_password but for compatibility it is not.
         if must_auth and not skip_auth:
 
             if not os_username and not os_user_id:
                 raise exc.CommandError(
                     _("You must provide a username "
                       "or user ID via --os-username, --os-user-id, "
                       "env[OS_USERNAME] or env[OS_USER_ID]"))
 
             if not any([os_project_name, os_project_id]):
                 raise exc.CommandError(_("You must provide a project name or"
                                          " project ID via --os-project-name,"
                                          " --os-project-id, env[OS_PROJECT_ID]"
                                          " or env[OS_PROJECT_NAME]. You may"
                                          " use os-project and os-tenant"
                                          " interchangeably."))
 
             if not os_auth_url:
                 raise exc.CommandError(
                     _("You must provide an auth url "
                       "via either --os-auth-url or env[OS_AUTH_URL]."))
 
             with utils.record_time(self.times, args.timings,
                                    'auth_url', args.os_auth_url):
                 keystone_session = (
                     loading.load_session_from_argparse_arguments(args))
                 keystone_auth = (
                     loading.load_auth_from_argparse_arguments(args))
 
         if (not skip_auth and
                 not any([os_project_name, os_project_id])):
             raise exc.CommandError(_("You must provide a project name or"
                                      " project id via --os-project-name,"
                                      " --os-project-id, env[OS_PROJECT_ID]"
                                      " or env[OS_PROJECT_NAME]. You may"
                                      " use os-project and os-tenant"
                                      " interchangeably."))
 
         if not os_auth_url and not skip_auth:
             raise exc.CommandError(
                 _("You must provide an auth url "
                   "via either --os-auth-url or env[OS_AUTH_URL]"))
 
         additional_kwargs = {}
         if osprofiler_profiler:
             additional_kwargs["profile"] = args.profile
 
         # This client is just used to discover api version. Version API needn't
         # microversion, so we just pass version 2 at here.
         self.cs = client.Client(
             api_versions.APIVersion("2.0"),
             os_username, os_password, project_id=os_project_id,
             project_name=os_project_name, user_id=os_user_id,
             auth_url=os_auth_url, insecure=insecure,
             region_name=os_region_name, endpoint_type=endpoint_type,
             extensions=self.extensions, service_type=service_type,
             service_name=service_name, auth_token=auth_token,
             timings=args.timings, endpoint_override=endpoint_override,
             os_cache=os_cache, http_log_debug=args.debug,
             cacert=cacert, cert=cert, timeout=timeout,
             session=keystone_session, auth=keystone_auth,
             logger=self.client_logger,
             project_domain_id=os_project_domain_id,
             project_domain_name=os_project_domain_name,
             user_domain_id=os_user_domain_id,
             user_domain_name=os_user_domain_name,
             **additional_kwargs)
 
         if not skip_auth:
             if not api_version.is_latest():
                 if api_version > api_versions.APIVersion("2.0"):
                     if not api_version.matches(novaclient.API_MIN_VERSION,
                                                novaclient.API_MAX_VERSION):
                         raise exc.CommandError(
                             _("The specified version isn't supported by "
                               "client. The valid version range is '%(min)s' "
                               "to '%(max)s'") % {
                                 "min": novaclient.API_MIN_VERSION.get_string(),
                                 "max": novaclient.API_MAX_VERSION.get_string()}
                        )
            api_version = api_versions.discover_version(self.cs, api_version)

        # build available subcommands based on version
        self.extensions = client.discover_extensions(api_version)
        self._run_extension_hooks('__pre_parse_args__')

        subcommand_parser = self.get_subcommand_parser(
            api_version, do_help=do_help, argv=argv)
        self.parser = subcommand_parser

        if args.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)
        self._run_extension_hooks('__post_parse_args__', args)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        if not args.service_type:
            service_type = (utils.get_service_type(args.func) or
                            DEFAULT_NOVA_SERVICE_TYPE)

        if utils.isunauthenticated(args.func):
            # NOTE(alex_xu): We need authentication for discover microversion.
            # But the subcommands may needn't it. If the subcommand needn't,
            # we clear the session arguments.
            keystone_session = None
            keystone_auth = None

        # Recreate client object with discovered version.
        self.cs = client.Client(
            api_version,
            os_username, os_password, project_id=os_project_id,
            project_name=os_project_name, user_id=os_user_id,
             auth_url=os_auth_url, insecure=insecure,
             region_name=os_region_name, endpoint_type=endpoint_type,
             extensions=self.extensions, service_type=service_type,
             service_name=service_name, auth_token=auth_token,
             timings=args.timings, endpoint_override=endpoint_override,
             os_cache=os_cache, http_log_debug=args.debug,
             cacert=cacert, cert=cert, timeout=timeout,
             session=keystone_session, auth=keystone_auth,
             project_domain_id=os_project_domain_id,
             project_domain_name=os_project_domain_name,
             user_domain_id=os_user_domain_id,
             user_domain_name=os_user_domain_name)
 
         # Now check for the password/token of which pieces of the
         # identifying keyring key can come from the underlying client
         if must_auth:
             helper = SecretsHelper(args, self.cs.client)
             self.cs.client.keyring_saver = helper
 
             tenant_id = helper.tenant_id
             # Allow commandline to override cache
             if not auth_token:
                 auth_token = helper.auth_token
             endpoint_override = endpoint_override or helper.management_url
             if tenant_id and auth_token and endpoint_override:
                 self.cs.client.tenant_id = tenant_id
                 self.cs.client.auth_token = auth_token
                 self.cs.client.management_url = endpoint_override
                 self.cs.client.password_func = lambda: helper.password
             else:
                 # We're missing something, so auth with user/pass and save
                 # the result in our helper.
                 self.cs.client.password = helper.password
 
         args.func(self.cs, args)
 
         if osprofiler_profiler and args.profile:
             trace_id = osprofiler_profiler.get().get_base_id()
             print("To display trace use the command:\n\n"
                   "  osprofiler trace show --html %s " % trace_id)
 
         if args.timings:
             self._dump_timings(self.times + self.cs.get_timings())
```

看到最后调用 `args.func(self.cs, args)`

在代码中加入一行

        args.func(self.cs, args)
        print('args.func', args.func)

执行 `nova list`，args.func 是 do_list 函数

```
args.func: <function do_list at 0x2f9db90>
```

找到 `novaclient/v2/shell.py`

```python
def do_list(cs, args):
    """List servers."""
    imageid = None
    flavorid = None
    if args.image:
        imageid = _find_image(cs, args.image).id
    if args.flavor:
        flavorid = _find_flavor(cs, args.flavor).id
    # search by tenant or user only works with all_tenants
    if args.tenant or args.user:
        args.all_tenants = 1
    search_opts = {
        'all_tenants': args.all_tenants,
        'reservation_id': args.reservation_id,
        'ip': args.ip,
        'ip6': args.ip6,
        'name': args.name,
        'image': imageid,
        'flavor': flavorid,
        'status': args.status,
        'tenant_id': args.tenant,
        'user_id': args.user,
        'host': args.host,
        'deleted': args.deleted,
        'instance_name': args.instance_name,
        'changes-since': args.changes_since}

    for arg in ('tags', "tags-any", 'not-tags', 'not-tags-any'):
        if arg in args:
            search_opts[arg] = getattr(args, arg)

    filters = {'security_groups': utils.format_security_groups}

    # In microversion 2.47 we started embedding flavor info in server details.
    have_embedded_flavor_info = (
        cs.api_version >= api_versions.APIVersion('2.47'))
    # If we don't have embedded flavor info then we only report the flavor id
    # rather than looking up the rest of the information.
    if not have_embedded_flavor_info:
        filters['flavor'] = lambda f: f['id']

    id_col = 'ID'

    detailed = not args.minimal

    sort_keys = []
    sort_dirs = []
    if args.sort:
        for sort in args.sort.split(','):
            sort_key, _sep, sort_dir = sort.partition(':')
            if not sort_dir:
                sort_dir = 'desc'
            elif sort_dir not in ('asc', 'desc'):
                raise exceptions.CommandError(_(
                    'Unknown sort direction: %s') % sort_dir)
            sort_keys.append(sort_key)
            sort_dirs.append(sort_dir)

    if search_opts['changes-since']:
        try:
            timeutils.parse_isotime(search_opts['changes-since'])
        except ValueError:
            raise exceptions.CommandError(_('Invalid changes-since value: %s')
                                          % search_opts['changes-since'])

    servers = cs.servers.list(detailed=detailed,
                              search_opts=search_opts,
                              sort_keys=sort_keys,
                              sort_dirs=sort_dirs,
                              marker=args.marker,
                              limit=args.limit)
    convert = [('OS-EXT-SRV-ATTR:host', 'host'),
               ('OS-EXT-STS:task_state', 'task_state'),
               ('OS-EXT-SRV-ATTR:instance_name', 'instance_name'),
               ('OS-EXT-STS:power_state', 'power_state'),
               ('hostId', 'host_id')]
    _translate_keys(servers, convert)
    _translate_extended_states(servers)

    formatters = {}
    cols = []
    fmts = {}

    # For detailed lists, if we have embedded flavor information then replace
    # the "flavor" attribute with more detailed information.
    if detailed and have_embedded_flavor_info:
        _expand_dict_attr(servers, 'flavor')

    if servers:
        cols, fmts = _get_list_table_columns_and_formatters(
            args.fields, servers, exclude_fields=('id',), filters=filters)

    if args.minimal:
        columns = [
            id_col,
            'Name']
    elif cols:
        columns = [id_col] + cols
        formatters.update(fmts)
    else:
        columns = [
            id_col,
            'Name',
            'Status',
            'Task State',
            'Power State',
            'Networks'
        ]
        # If getting the data for all tenants, print
        # Tenant ID as well
        if search_opts['all_tenants']:
            columns.insert(2, 'Tenant ID')
        if search_opts['changes-since']:
            columns.append('Updated')
    formatters['Networks'] = utils.format_servers_list_networks
    sortby_index = 1
    if args.sort:
        sortby_index = None
    utils.print_list(servers, columns,
                     formatters, sortby_index=sortby_index)
```

可以看到

```python
servers = cs.servers.list(detailed=detailed,
                          search_opts=search_opts,
                          sort_keys=sort_keys,
                          sort_dirs=sort_dirs,
                          marker=args.marker,
                          limit=args.limit)
```

其中 cs 在 `novaclient/shell.py` 的`OpenStackComputeShell`中定义：

```python
 self.cs = client.Client(
     api_versions.APIVersion("2.0"),
     os_username, os_password, project_id=os_project_id,
     project_name=os_project_name, user_id=os_user_id,
     auth_url=os_auth_url, insecure=insecure,
     region_name=os_region_name, endpoint_type=endpoint_type,
     extensions=self.extensions, service_type=service_type,
     service_name=service_name, auth_token=auth_token,
     timings=args.timings, endpoint_override=endpoint_override,
     os_cache=os_cache, http_log_debug=args.debug,
     cacert=cacert, cert=cert, timeout=timeout,
     session=keystone_session, auth=keystone_auth,
     logger=self.client_logger,
     project_domain_id=os_project_domain_id,
     project_domain_name=os_project_domain_name,
     user_domain_id=os_user_domain_id,
     user_domain_name=os_user_domain_name,
     **additional_kwargs)
```

到 `novaclient/v2/client.py`看 Client 的定义：

```python
class Client(object):
    """Top-level object to access the OpenStack Compute API.

    .. warning:: All scripts and projects should not initialize this class
      directly. It should be done via `novaclient.client.Client` interface.
    """

    def __init__(self,
                 api_version=None,
                 auth=None,
                 auth_token=None,
                 auth_url=None,
                 cacert=None,
                 cert=None,
                 direct_use=True,
                 endpoint_override=None,
                 endpoint_type='publicURL',
                 extensions=None,
                 http_log_debug=False,
                 insecure=False,
                 logger=None,
                 os_cache=False,
                 password=None,
                 project_domain_id=None,
                 project_domain_name=None,
                 project_id=None,
                 project_name=None,
                 region_name=None,
                 service_name=None,
                 service_type='compute',
                 session=None,
                 timeout=None,
                 timings=False,
                 user_domain_id=None,
                 user_domain_name=None,
                 user_id=None,
                 username=None,
                 **kwargs):
        """Initialization of Client object.

        :param api_version: Compute API version
        :type api_version: novaclient.api_versions.APIVersion
        :param str auth: Auth
        :param str auth_token: Auth token
        :param str auth_url: Auth URL
        :param str cacert: ca-certificate
        :param str cert: certificate
        :param bool direct_use: Inner variable of novaclient. Do not use it
            outside novaclient. It's restricted.
        :param str endpoint_override: Bypass URL
        :param str endpoint_type: Endpoint Type
        :param str extensions: Extensions
        :param bool http_log_debug: Enable debugging for HTTP connections
        :param bool insecure: Allow insecure
        :param logging.Logger logger: Logger instance to be used for all
            logging stuff
        :param str password: User password
        :param bool os_cache: OS cache
        :param str project_domain_id: ID of project domain
        :param str project_domain_name: Name of project domain
        :param str project_id: Project/Tenant ID
        :param str project_name: Project/Tenant name
        :param str region_name: Region Name
        :param str service_name: Service Name
        :param str service_type: Service Type
        :param str session: Session
        :param float timeout: API timeout, None or 0 disables
        :param bool timings: Timings
        :param str user_domain_id: ID of user domain
        :param str user_domain_name: Name of user domain
        :param str user_id: User ID
        :param str username: Username
        """
        if direct_use:
            raise exceptions.Forbidden(
                403, _("'novaclient.v2.client.Client' is not designed to be "
                       "initialized directly. It is inner class of "
                       "novaclient. You should use "
                       "'novaclient.client.Client' instead. Related lp "
                       "bug-report: 1493576"))

        # NOTE(cyeoh): In the novaclient context (unlike Nova) the
        # project_id is not the same as the tenant_id. Here project_id
        # is a name (what the Nova API often refers to as a project or
        # tenant name) and tenant_id is a UUID (what the Nova API
        # often refers to as a project_id or tenant_id).

        self.project_id = project_id
        self.project_name = project_name
        self.user_id = user_id
        self.flavors = flavors.FlavorManager(self)
        self.flavor_access = flavor_access.FlavorAccessManager(self)
        self.glance = images.GlanceManager(self)
        self.limits = limits.LimitsManager(self)
        self.servers = servers.ServerManager(self)
        self.versions = versions.VersionManager(self)

        # extensions
        self.agents = agents.AgentsManager(self)
        self.cloudpipe = cloudpipe.CloudpipeManager(self)
        self.certs = certs.CertificateManager(self)
        self.volumes = volumes.VolumeManager(self)
        self.keypairs = keypairs.KeypairManager(self)
        self.neutron = networks.NeutronManager(self)
        self.quota_classes = quota_classes.QuotaClassSetManager(self)
        self.quotas = quotas.QuotaSetManager(self)
        self.usage = usage.UsageManager(self)
        self.virtual_interfaces = \
            virtual_interfaces.VirtualInterfaceManager(self)
        self.aggregates = aggregates.AggregateManager(self)
        self.hosts = hosts.HostManager(self)
        self.hypervisors = hypervisors.HypervisorManager(self)
        self.hypervisor_stats = hypervisors.HypervisorStatsManager(self)
        self.services = services.ServiceManager(self)
        self.os_cache = os_cache
        self.availability_zones = \
            availability_zones.AvailabilityZoneManager(self)
        self.server_groups = server_groups.ServerGroupsManager(self)
        self.server_migrations = \
            server_migrations.ServerMigrationsManager(self)

        # V2.0 extensions:
        # NOTE(andreykurilin): tenant_networks extension is
        #   deprecated now, which is why it is not initialized by default.
        self.assisted_volume_snapshots = \
            assisted_volume_snapshots.AssistedSnapshotManager(self)
        self.cells = cells.CellsManager(self)
        self.instance_action = instance_action.InstanceActionManager(self)
        self.list_extensions = list_extensions.ListExtManager(self)
        self.migrations = migrations.MigrationManager(self)
        self.server_external_events = \
            server_external_events.ServerExternalEventManager(self)

        self.logger = logger or logging.getLogger(__name__)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                # do not import extensions from contrib directory twice.
                if extension.name in contrib.V2_0_EXTENSIONS:
                    # NOTE(andreykurilin): this message looks more like
                    #   warning or note, but it is not critical, so let's do
                    #   not flood "warning" logging level and use just debug..
                    self.logger.debug("Nova 2.0 extenstion '%s' is auto-loaded"
                                      " by default. You do not need to specify"
                                      " it manually.", extension.name)
                    continue
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

        self.client = client._construct_http_client(
            api_version=api_version,
            auth=auth,
            auth_token=auth_token,
            auth_url=auth_url,
            cacert=cacert,
            cert=cert,
            endpoint_override=endpoint_override,
            endpoint_type=endpoint_type,
            http_log_debug=http_log_debug,
            insecure=insecure,
            logger=self.logger,
            os_cache=self.os_cache,
            password=password,
            project_domain_id=project_domain_id,
            project_domain_name=project_domain_name,
            project_id=project_id,
            project_name=project_name,
            region_name=region_name,
            service_name=service_name,
            service_type=service_type,
            session=session,
            timeout=timeout,
            timings=timings,
            user_domain_id=user_domain_id,
            user_domain_name=user_domain_name,
            user_id=user_id,
            username=username,
            **kwargs)

    @property
    def api_version(self):
        return self.client.api_version

    @api_version.setter
    def api_version(self, value):
        self.client.api_version = value

    @property
    def projectid(self):
        self.logger.warning(_("Property 'projectid' is deprecated since "
                              "Ocata. Use 'project_name' instead."))
        return self.project_name

    @property
    def tenant_id(self):
        self.logger.warning(_("Property 'tenant_id' is deprecated since "
                              "Ocata. Use 'project_id' instead."))
        return self.project_id

    def __enter__(self):
        self.logger.warning(_("NovaClient instance can't be used as a "
                              "context manager since Ocata (deprecated "
                              "behaviour) since it is redundant in case of "
                              "SessionClient."))
        return self

    def __exit__(self, t, v, tb):
        # do not do anything
        pass

    def set_management_url(self, url):
        self.logger.warning(
            _("Method `set_management_url` is deprecated since Ocata. "
              "Use `endpoint_override` argument instead while initializing "
              "novaclient's instance."))
        self.client.set_management_url(url)

    def get_timings(self):
        return self.client.get_timings()

    def reset_timings(self):
        self.client.reset_timings()

    def authenticate(self):
        """Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.logger.warning(_(
            "Method 'authenticate' is deprecated since Ocata."))
```

看到  `self.servers = servers.ServerManager(self)`

找到`novaclient/v2/servers.py`

```python
class ServerManager(base.BootingManagerWithFind):
    resource_class = Server
	......
    def list(self, detailed=True, search_opts=None, marker=None, limit=None,
             sort_keys=None, sort_dirs=None):
        """
        Get a list of servers.

        :param detailed: Whether to return detailed server info (optional).
        :param search_opts: Search options to filter out servers which don't
            match the search_opts (optional). The search opts format is a
            dictionary of key / value pairs that will be appended to the query
            string.  For a complete list of keys see:
            https://developer.openstack.org/api-ref/compute/#list-servers
        :param marker: Begin returning servers that appear later in the server
                       list than that represented by this server id (optional).
        :param limit: Maximum number of servers to return (optional).
        :param sort_keys: List of sort keys
        :param sort_dirs: List of sort directions

        :rtype: list of :class:`Server`

        Examples:

        client.servers.list() - returns detailed list of servers

        client.servers.list(search_opts={'status': 'ERROR'}) -
        returns list of servers in error state.

        client.servers.list(limit=10) - returns only 10 servers

        """
        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in search_opts.items():
            if val:
                if isinstance(val, six.text_type):
                    val = val.encode('utf-8')
                qparams[opt] = val

        detail = ""
        if detailed:
            detail = "/detail"

        result = base.ListWithMeta([], None)
        while True:
            if marker:
                qparams['marker'] = marker

            if limit and limit != -1:
                qparams['limit'] = limit

            # Transform the dict to a sequence of two-element tuples in fixed
            # order, then the encoded string will be consistent in Python 2&3.
            if qparams or sort_keys or sort_dirs:
                # sort keys and directions are unique since the same parameter
                # key is repeated for each associated value
                # (ie, &sort_key=key1&sort_key=key2&sort_key=key3)
                items = list(qparams.items())
                if sort_keys:
                    items.extend(('sort_key', sort_key)
                                 for sort_key in sort_keys)
                if sort_dirs:
                    items.extend(('sort_dir', sort_dir)
                                 for sort_dir in sort_dirs)
                new_qparams = sorted(items, key=lambda x: x[0])
                query_string = "?%s" % parse.urlencode(new_qparams)
            else:
                query_string = ""

            servers = self._list("/servers%s%s" % (detail, query_string),
                                 "servers")
            result.extend(servers)
            result.append_request_ids(servers.request_ids)

            if limit and limit != -1:
                limit = max(limit - len(servers), 0)

            if not servers or limit == 0:
                break
            marker = result[-1].id
        return result
...
```

看到

```python
servers = self._list("/servers%s%s" % (detail, query_string),
                                 "servers")
```

找到 `novaclient/base.py`

```python
class Manager(HookableMixin):
    ……
    def _list(self, url, response_key, obj_class=None, body=None):
        if body:
            resp, body = self.api.client.post(url, body=body)
        else:
            resp, body = self.api.client.get(url)

        if obj_class is None:
            obj_class = self.resource_class

        data = body[response_key]
        # NOTE(ja): keystone returns values as list as {'values': [ ... ]}
        #           unlike other services which just return the list...
        if isinstance(data, dict):
            try:
                data = data['values']
            except KeyError:
                pass

        with self.completion_cache('human_id', obj_class, mode="w"):
            with self.completion_cache('uuid', obj_class, mode="w"):
                items = [obj_class(self, res, loaded=True)
                         for res in data if res]
                return ListWithMeta(items, resp)
```

根据上面 `list`  对  `_list` 的调用，可知 `url = '/servers/detail'`  ,  `body = None`

因此会执行

```python
resp, body = self.api.client.get(url)
```

直接打印，看一下 `self.api.client`  这个对象

```python
self.api:
<novaclient.v2.client.Client object at 0x3cf7d10>
self.api.client:
<novaclient.client.SessionClient object at 0x40a2350>
```

上面的  `novaclient/v2/client.py`  

```
self.servers = servers.ServerManager(self)
self.client = client._construct_http_client（
	……
	）
```

看一下 client._construct_http_client

`novaclient/client.py`

```python
def _construct_http_client(api_version=None,
                           ……
                           **kwargs):
    ……
    return SessionClient(api_version=api_version,
                         ……
                         **kwargs)
```

可见就是 `SessionClient`

```python
class SessionClient(adapter.LegacyJsonAdapter):

    client_name = 'python-novaclient'
    client_version = novaclient.__version__

    def __init__(self, *args, **kwargs):
        self.times = []
        self.timings = kwargs.pop('timings', False)
        self.api_version = kwargs.pop('api_version', None)
        self.api_version = self.api_version or api_versions.APIVersion()
        super(SessionClient, self).__init__(*args, **kwargs)

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        api_versions.update_headers(kwargs["headers"], self.api_version)

        # NOTE(dbelova): osprofiler_web.get_trace_id_headers does not add any
        # headers in case if osprofiler is not initialized.
        if osprofiler_web:
            kwargs['headers'].update(osprofiler_web.get_trace_id_headers())

        # NOTE(jamielennox): The standard call raises errors from
        # keystoneauth1, where we need to raise the novaclient errors.
        raise_exc = kwargs.pop('raise_exc', True)
        with utils.record_time(self.times, self.timings, method, url):
            resp, body = super(SessionClient, self).request(url,
                                                            method,
                                                            raise_exc=False,
                                                            **kwargs)

        # TODO(andreykurilin): uncomment this line, when we will be able to
        #   check only nova-related calls
        # api_versions.check_headers(resp, self.api_version)
        if raise_exc and resp.status_code >= 400:
            raise exceptions.from_response(resp, body, url, method)

        return resp, body

    def get_timings(self):
        return self.times

    def reset_timings(self):
        self.times = []

    @property
    def management_url(self):
        self.logger.warning(
            _("Property `management_url` is deprecated for SessionClient. "
              "Use `endpoint_override` instead."))
        return self.endpoint_override

    @management_url.setter
    def management_url(self, value):
        self.logger.warning(
            _("Property `management_url` is deprecated for SessionClient. "
              "It should be set via `endpoint_override` variable while class"
              " initialization."))
        self.endpoint_override = value
```

因为

```python
class SessionClient(adapter.LegacyJsonAdapter):
	……
    def request(self, url, method, **kwargs):
		……
        with utils.record_time(self.times, self.timings, method, url):
            resp, body = super(SessionClient, self).request(url,
                                                            method,
                                                            raise_exc=False,
                                                            **kwargs)
```

所以看父类 

`keystoneauth1/adapter.py`

```python
class LegacyJsonAdapter(Adapter):
    """Make something that looks like an old HTTPClient.

    A common case when using an adapter is that we want an interface similar to
    the HTTPClients of old which returned the body as JSON as well.

    You probably don't want this if you are starting from scratch.
    """

    def request(self, *args, **kwargs):
        headers = kwargs.setdefault('headers', {})
        headers.setdefault('Accept', 'application/json')

        try:
            kwargs['json'] = kwargs.pop('body')
        except KeyError:
            pass

        resp = super(LegacyJsonAdapter, self).request(*args, **kwargs)

        try:
            body = resp.json()
        except ValueError:
            body = None

        return resp, body

```

上面说到要执行`resp, body = self.api.client.get(url)`

所以找到 get 方法，get 调用了 `self.request(url, 'GET', **kwargs)`

`keystoneauth1/adapter.py`

```python

class Adapter(object):
    """An instance of a session with local variables.
    ……
    """
	def request(self, url, method, **kwargs):
        ……
        return self.session.request(url, method, **kwargs)
    
    def get(self, url, **kwargs):
        return self.request(url, 'GET', **kwargs)
```

`request`调用的是`self.session.request(url, method, **kwargs)`

接着看 session

`keystoneautth1/session.py`

```python
class Session(object):
    """Maintains client communication state and common functionality.

    As much as possible the parameters to this class reflect and are passed
    directly to the :mod:`requests` library.
    ……
    """
    def request(self, url, method, json=None, original_ip=None,
                user_agent=None, redirect=None, authenticated=None,
                endpoint_filter=None, auth=None, requests_auth=None,
                raise_exc=True, allow_reauth=True, log=True,
                endpoint_override=None, connect_retries=0, logger=_logger,
                allow={}, client_name=None, client_version=None,
                microversion=None, microversion_service_type=None,
                **kwargs):
        """Send an HTTP request with the specified characteristics.
        ……
        :returns: The response to the request.
        """
        headers = kwargs.setdefault('headers', dict())
        if microversion:
            self._set_microversion_headers(
                headers, microversion, microversion_service_type,
                endpoint_filter)

        if authenticated is None:
            authenticated = bool(auth or self.auth)

        if authenticated:
            auth_headers = self.get_auth_headers(auth)

            if auth_headers is None:
                msg = 'No valid authentication is available'
                raise exceptions.AuthorizationFailure(msg)

            headers.update(auth_headers)

        if osprofiler_web:
            headers.update(osprofiler_web.get_trace_id_headers())

        # if we are passed a fully qualified URL and an endpoint_filter we
        # should ignore the filter. This will make it easier for clients who
        # want to overrule the default endpoint_filter data added to all client
        # requests. We check fully qualified here by the presence of a host.
        if not urllib.parse.urlparse(url).netloc:
            base_url = None

            if endpoint_override:
                base_url = endpoint_override % _StringFormatter(self, auth)
            elif endpoint_filter:
                base_url = self.get_endpoint(auth, allow=allow,
                                             **endpoint_filter)

            if not base_url:
                raise exceptions.EndpointNotFound()

            url = '%s/%s' % (base_url.rstrip('/'), url.lstrip('/'))

        if self.cert:
            kwargs.setdefault('cert', self.cert)

        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        if user_agent:
            headers['User-Agent'] = user_agent
        elif self.user_agent:
            user_agent = headers.setdefault('User-Agent', self.user_agent)
        else:
            # Per RFC 7231 Section 5.5.3, identifiers in a user-agent should be
            # ordered by decreasing significance.  If a user sets their product
            # that value will be used. Otherwise we attempt to derive a useful
            # product value. The value will be prepended it to the KSA version,
            # requests version, and then the Python version.

            agent = []

            if self.app_name and self.app_version:
                agent.append('%s/%s' % (self.app_name, self.app_version))
            elif self.app_name:
                agent.append(self.app_name)

            for additional in self.additional_user_agent:
                agent.append('%s/%s' % additional)

            if client_name and client_version:
                agent.append('%s/%s' % (client_name, client_version))
            elif client_name:
                agent.append(client_name)

            if not agent:
                # NOTE(jamielennox): determine_user_agent will return an empty
                # string on failure so checking for None will ensure it is only
                # called once even on failure.
                if self._determined_user_agent is None:
                    self._determined_user_agent = _determine_user_agent()

                if self._determined_user_agent:
                    agent.append(self._determined_user_agent)

            agent.append(DEFAULT_USER_AGENT)
            user_agent = headers.setdefault('User-Agent', ' '.join(agent))

        if self.original_ip:
            headers.setdefault('Forwarded',
                               'for=%s;by=%s' % (self.original_ip, user_agent))

        if json is not None:
            headers.setdefault('Content-Type', 'application/json')
            kwargs['data'] = self._json.encode(json)

        for k, v in self.additional_headers.items():
            headers.setdefault(k, v)

        kwargs.setdefault('verify', self.verify)

        if requests_auth:
            kwargs['auth'] = requests_auth

        # Query parameters that are included in the url string will
        # be logged properly, but those sent in the `params` parameter
        # (which the requests library handles) need to be explicitly
        # picked out so they can be included in the URL that gets loggged.
        query_params = kwargs.get('params', dict())

        if log:
            self._http_log_request(url, method=method,
                                   data=kwargs.get('data'),
                                   headers=headers,
                                   query_params=query_params,
                                   logger=logger)

        # Force disable requests redirect handling. We will manage this below.
        kwargs['allow_redirects'] = False

        if redirect is None:
            redirect = self.redirect

        send = functools.partial(self._send_request,
                                 url, method, redirect, log, logger,
                                 connect_retries)

        try:
            connection_params = self.get_auth_connection_params(auth=auth)
        except exceptions.MissingAuthPlugin:
            # NOTE(jamielennox): If we've gotten this far without an auth
            # plugin then we should be happy with allowing no additional
            # connection params. This will be the typical case for plugins
            # anyway.
            pass
        else:
            if connection_params:
                kwargs.update(connection_params)

        resp = send(**kwargs)

        # log callee and caller request-id for each api call
        if log:
            # service_name should be fetched from endpoint_filter if it is not
            # present then use service_type as service_name.
            service_name = None
            if endpoint_filter:
                service_name = endpoint_filter.get('service_name')
                if not service_name:
                    service_name = endpoint_filter.get('service_type')

            # Nova uses 'x-compute-request-id' and other services like
            # Glance, Cinder etc are using 'x-openstack-request-id' to store
            # request-id in the header
            request_id = (resp.headers.get('x-openstack-request-id') or
                          resp.headers.get('x-compute-request-id'))
            if request_id:
                logger.debug('%(method)s call to %(service_name)s for '
                             '%(url)s used request id '
                             '%(response_request_id)s',
                             {'method': resp.request.method,
                              'service_name': service_name,
                              'url': resp.url,
                              'response_request_id': request_id})

        # handle getting a 401 Unauthorized response by invalidating the plugin
        # and then retrying the request. This is only tried once.
        if resp.status_code == 401 and authenticated and allow_reauth:
            if self.invalidate(auth):
                auth_headers = self.get_auth_headers(auth)

                if auth_headers is not None:
                    headers.update(auth_headers)
                    resp = send(**kwargs)

        if raise_exc and resp.status_code >= 400:
            logger.debug('Request returned failure status: %s',
                         resp.status_code)
            raise exceptions.from_response(resp, method, url)

        return resp
```

看到这一段

```python
        if authenticated is None:
            authenticated = bool(auth or self.auth)

        if authenticated:
            auth_headers = self.get_auth_headers(auth)

            if auth_headers is None:
                msg = 'No valid authentication is available'
                raise exceptions.AuthorizationFailure(msg)

            headers.update(auth_headers)
```

打印`auth_headers`

```
{'X-Auth-Token': 'gAAAAABat2oxbu6IZkOBAnHCZkcaqLoerNfw4P7SjstWSzSy4RCMjvkpkaaMGDDUMo5ndDEec8L6LNTmBSEsCePcAuajTRp3EpHJFiExFegk-HCgFqI1NiY3xqojATJh292n0yPamjG8_PaZpmbbH_T0xaoEb0OaXwUrwyxobLknho2ojAW7AHU'}
```

`auth_headers = self.get_auth_headers(auth)`   这一行就是在获取 token

找到 `get_auth_headers`

```python
    def _auth_required(self, auth, msg):
        if not auth:
            auth = self.auth

        if not auth:
            msg_fmt = 'An auth plugin is required to %s'
            raise exceptions.MissingAuthPlugin(msg_fmt % msg)

        return auth
    def get_auth_headers(self, auth=None, **kwargs):
        """Return auth headers as provided by the auth plugin.

        :param auth: The auth plugin to use for token. Overrides the plugin
                     on the session. (optional)
        :type auth: keystoneauth1.plugin.BaseAuthPlugin

        :raises keystoneauth1.exceptions.auth.AuthorizationFailure:
            if a new token fetch fails.
        :raises keystoneauth1.exceptions.auth_plugins.MissingAuthPlugin:
            if a plugin is not available.

        :returns: Authentication headers or None for failure.
        :rtype: :class:`dict`
        """
        auth = self._auth_required(auth, 'fetch a token')
        return auth.get_headers(self, **kwargs)
    
```

打印一下 auth，得到

```
<keystoneauth1.identity.generic.password.Password object at 0x34bf8d0>
```

继续看，执行 `auth.get_headers(self, **kwargs)`

`keystoneauth1/identity/generic/password.py`

```python
class Password(base.BaseGenericPlugin):
	……
```

并没有 `get_headers` 方法，因此去他的父类找

`keystoneauth1/identity/generic/base.py:BaseGenericPlugin(base.BaseIdentityPlugin)`

`keystoneauth1/identity/base.py:BaseIdentityPlugin(plugin.BaseAuthPlugin)`

最后找到 `keystoneauth1/plugin.py`

```python
class BaseAuthPlugin(object):
    """The basic structure of an authentication plugin.

    .. note::
        See :doc:`/authentication-plugins` for a description of plugins
        provided by this library.

    """
    def get_headers(self, session, **kwargs):
        """Fetch authentication headers for message.

        This is a more generalized replacement of the older get_token to allow
        plugins to specify different or additional authentication headers to
        the OpenStack standard 'X-Auth-Token' header.

        How the authentication headers are obtained is up to the plugin. If the
        headers are still valid they may be re-used, retrieved from cache or
        the plugin may invoke an authentication request against a server.

        The default implementation of get_headers calls the `get_token` method
        to enable older style plugins to continue functioning unchanged.
        Subclasses should feel free to completely override this function to
        provide the headers that they want.

        There are no required kwargs. They are passed directly to the auth
        plugin and they are implementation specific.

        Returning None will indicate that no token was able to be retrieved and
        that authorization was a failure. Adding no authentication data can be
        achieved by returning an empty dictionary.

        :param session: The session object that the auth_plugin belongs to.
        :type session: keystoneauth1.session.Session

        :returns: Headers that are set to authenticate a message or None for
                  failure. Note that when checking this value that the empty
                  dict is a valid, non-failure response.
        :rtype: dict
        """
        token = self.get_token(session)

        if not token:
            return None

        return {IDENTITY_AUTH_HEADER_NAME: token}
    
    def get_token(self, session, **kwargs):
        """Obtain a token.

        How the token is obtained is up to the plugin. If it is still valid
        it may be re-used, retrieved from cache or invoke an authentication
        request against a server.

        There are no required kwargs. They are passed directly to the auth
        plugin and they are implementation specific.

        Returning None will indicate that no token was able to be retrieved.

        This function is misplaced as it should only be required for auth
        plugins that use the 'X-Auth-Token' header. However due to the way
        plugins evolved this method is required and often called to trigger an
        authentication request on a new plugin.

        When implementing a new plugin it is advised that you implement this
        method, however if you don't require the 'X-Auth-Token' header override
        the `get_headers` method instead.

        :param session: A session object so the plugin can make HTTP calls.
        :type session: keystoneauth1.session.Session

        :return: A token to use.
        :rtype: string
        """
        return None
```

