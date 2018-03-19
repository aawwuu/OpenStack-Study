nova list

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
    ...
            self.servers = servers.ServerManager(self)
    ...
```

找到`novaclient/v2/servers.py`

```python
class ServerManager(base.BootingManagerWithFind):
    resource_class = Server
...
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

找到调用接口

```python
result = base.ListWithMeta([], None)
servers = self._list("/servers%s%s" % (detail, query_string),
                                 "servers")
result.extend(servers)
```

位于 `novaclient/base.py`

```python
class Manager(HookableMixin):
    """Manager for API service.

    Managers interact with a particular type of API (servers, flavors, images,
    etc.) and provide CRUD operations for them.
    """
    resource_class = None
    cache_lock = threading.RLock()

    def __init__(self, api):
        self.api = api

    @property
    def client(self):
        return self.api.client

    @property
    def api_version(self):
        return self.api.api_version

    def _list(self, url, response_key, obj_class=None, body=None,
              filters=None):
        if filters:
            url = utils.get_url_with_filter(url, filters)
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

