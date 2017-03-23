# -*- coding: utf-8 -*-
#
#    bitcoinlib - Compact Python Bitcoin Library
#    Network Definitions
#    © 2016 November - 1200 Web Development <http://1200wd.com/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import json
import binascii
import math
import logging
from bitcoinlib.main import DEFAULT_SETTINGSDIR, CURRENT_INSTALLDIR_DATA
from bitcoinlib.encoding import to_hexstring, normalize_var


_logger = logging.getLogger(__name__)


DEFAULT_NETWORK = 'bitcoin'

def read_network_definitions():
    try:
        fn = DEFAULT_SETTINGSDIR + "/networks.json"
        f = open(fn, "r")
    except FileNotFoundError:
        fn = CURRENT_INSTALLDIR_DATA + "/networks.json"
        f = open(fn, "r")

    try:
        network_definitions = json.loads(f.read())
    except json.decoder.JSONDecodeError as e:
        errstr = "Error reading provider definitions from %s: %s" % (fn, e)
        _logger.warning(errstr)
        raise NetworkError(errstr)
    f.close()
    return network_definitions

NETWORK_DEFINITIONS = read_network_definitions()


def _format_value(field, value):
    if field[:6] == 'prefix':
        return binascii.unhexlify(value)
    elif field == 'denominator':
        return float(value)
    else:
        return value


def network_values_for(field, output_as='default'):
    r = [_format_value(field, nv[field]) for nv in NETWORK_DEFINITIONS.values()]
    if output_as == 'str':
        return [normalize_var(i) for i in r]
    elif output_as == 'hex':
        return [to_hexstring(i) for i in r]
    else:
        return r


def network_by_value(field, value):
    value = to_hexstring(value).upper()
    return [nv for nv in NETWORK_DEFINITIONS if NETWORK_DEFINITIONS[nv][field].upper() == value]


def network_defined(network):
    if network not in list(NETWORK_DEFINITIONS.keys()):
        return False
    return True


class NetworkError(Exception):
    def __init__(self, msg=''):
        self.msg = msg
        _logger.error(msg)

    def __str__(self):
        return self.msg


class Network:

    def __init__(self, network_name=DEFAULT_NETWORK):
        self.network_name = network_name
        self.prefix_wif = binascii.unhexlify(NETWORK_DEFINITIONS[network_name]['prefix_wif'])
        self.currency_code = NETWORK_DEFINITIONS[network_name]['currency_code']
        self.currency_symbol = NETWORK_DEFINITIONS[network_name]['currency_symbol']
        self.prefix_address_p2sh = binascii.unhexlify(NETWORK_DEFINITIONS[network_name]['prefix_address_p2sh'])
        self.prefix_address = binascii.unhexlify(NETWORK_DEFINITIONS[network_name]['prefix_address'])
        self.prefix_hdkey_public = binascii.unhexlify(NETWORK_DEFINITIONS[network_name]['prefix_hdkey_public'])
        self.description = NETWORK_DEFINITIONS[network_name]['description']
        self.prefix_hdkey_private = binascii.unhexlify(NETWORK_DEFINITIONS[network_name]['prefix_hdkey_private'])
        self.denominator = NETWORK_DEFINITIONS[network_name]['denominator']
        self.bip44_cointype = NETWORK_DEFINITIONS[network_name]['bip44_cointype']

        # This could be more shorter and more flexible with this code, but this gives 'Unresolved attributes' warnings
        # for f in list(NETWORK_DEFINITIONS[network_name].keys()):
        #     exec("self.%s = NETWORK_DEFINITIONS[network_name]['%s']" % (f, f))

    def __repr__(self):
        return "<Network: %s>" % self.network_name

    def print_value(self, value):
        symb = self.currency_code
        denominator = self.denominator
        denominator_size = -int(math.log10(denominator))
        balance = round(value * denominator, denominator_size)
        format_str = "%%.%df %%s" % denominator_size
        return format_str % (balance, symb)


if __name__ == '__main__':
    #
    # NETWORK EXAMPLES
    #

    network = Network('bitcoin')
    print("\n=== Get all WIF prefixes ===")
    print("WIF Prefixes: %s" % network_values_for('prefix_wif'))

    print("\n=== Get all HDkey private prefixes ===")
    print("HDkey private prefixes: %s" % network_values_for('prefix_hdkey_private', output_as='str'))

    print("\n=== Get network(s) for WIF prefix B0 ===")
    print("WIF Prefixes: %s" % network_by_value('prefix_wif', 'B0'))

    print("\n=== Get HD key private prefix for current network ===")
    print("self.prefix_hdkey_private: %s" % network.prefix_hdkey_private)

    print("\n=== Network parameters ===")
    for k in network.__dir__():
        if k[:1] != '_':
            v = eval('network.%s' % k)
            if not callable(v):
                print("%25s: %s" % (k, v))