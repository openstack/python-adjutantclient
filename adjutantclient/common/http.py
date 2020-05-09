# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from keystoneauth1 import adapter
from keystoneauth1.identity import v3
from keystoneauth1 import session as ks_session
from oslo_utils import importutils
import requests

from adjutantclient._i18n import _
from adjutantclient import exc

LOG = logging.getLogger(__name__)
USER_AGENT = 'python-adjutantclient'
CHUNKSIZE = 1024 * 64  # 64kB
SENSITIVE_HEADERS = ('X-Auth-Token',)
osprofiler_web = importutils.try_import("osprofiler.web")


def get_response_body(resp):
    body = resp.content
    if 'application/json' in resp.headers.get('content-type', ''):
        try:
            body = resp.json()
        except ValueError:
            LOG.error('Could not decode response body as JSON')
    else:
        body = None
    return body


def get_system_ca_file():
    """Return path to system default CA file."""
    # Standard CA file locations for Debian/Ubuntu, RedHat/Fedora,
    # Suse, FreeBSD/OpenBSD, MacOSX, and the bundled ca
    ca_path = ['/etc/ssl/certs/ca-certificates.crt',
               '/etc/pki/tls/certs/ca-bundle.crt',
               '/etc/ssl/ca-bundle.pem',
               '/etc/ssl/cert.pem',
               '/System/Library/OpenSSL/certs/cacert.pem',
               requests.certs.where()]
    for ca in ca_path:
        LOG.debug("Looking for ca file %s", ca)
        if os.path.exists(ca):
            LOG.debug("Using ca file %s", ca)
            return ca
    LOG.warning("System ca file could not be found.")


class SessionClient(adapter.LegacyJsonAdapter):
    """HTTP client based on Keystone client session."""

    def request(self, url, method, **kwargs):
        redirect = kwargs.get('redirect')
        kwargs.setdefault('user_agent', USER_AGENT)

        if 'data' in kwargs:
            kwargs['json'] = kwargs.pop('data')

        resp, body = super(SessionClient, self).request(
            url, method,
            raise_exc=False,
            **kwargs)

        if 400 <= resp.status_code < 600:
            raise exc.from_response(resp)
        elif resp.status_code in (301, 302, 305):
            if redirect:
                location = resp.headers.get('location')
                path = self.strip_endpoint(location)
                resp = self.request(path, method, **kwargs)
        elif resp.status_code == 300:
            raise exc.from_response(resp)

        return resp

    def credentials_headers(self):
        return {}

    def strip_endpoint(self, location):
        if location is None:
            message = _("Location not returned with 302")
            raise exc.InvalidEndpoint(message=message)
        if (self.endpoint_override is not None and
                location.lower().startswith(self.endpoint_override.lower())):
            return location[len(self.endpoint_override):]
        else:
            return location


def _construct_http_client(endpoint=None, username=None, password=None,
                           include_pass=None, endpoint_type=None,
                           auth_url=None, **kwargs):
    session = kwargs.pop('session', None)
    auth = kwargs.pop('auth', None)

    if not session:
        if not auth and password:
            auth = v3.Password(auth_url=auth_url,
                               username=username,
                               password=password,
                               **kwargs)
            kwargs.pop('project_id', None)
            kwargs.pop('project_name', None)
            kwargs.pop('domain_id', None)
            kwargs.pop('domain_name', None)
            kwargs.pop('project_domain_id', None)
            kwargs.pop('project_domain_name', None)
            kwargs.pop('user_domain_id', None)
            kwargs.pop('user_domain_name', None)

        ca_path = kwargs.get('ca_file') or get_system_ca_file()
        session = ks_session.Session(auth=auth,
                                     verify=ca_path)

    if 'endpoint_override' not in kwargs and endpoint:
        kwargs['endpoint_override'] = endpoint

    if 'service_type' not in kwargs:
        kwargs['service_type'] = 'admin-logic'

    if 'interface' not in kwargs and endpoint_type:
        kwargs['interface'] = endpoint_type

    return SessionClient(session, auth=auth, **kwargs)
