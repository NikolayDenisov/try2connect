#!/usr/bin/env python3

import argparse
import configparser
import json
import logging
import os
import shutil
from urllib import parse

from dns import resolver
from gevent import socket

config = configparser.ConfigParser()
config.read('config.ini')


class Cache:
    """
    Class for working with cache records. Format 'domain': 'ip'
    """

    def __init__(self, host):
        self.host = host
        self.raw_cache = {}
        if not os.path.exists(config['DIRS']['CACHED_ADDR_FILE']):
            logging.info('Create cache-file with IP-address')
            os.system('touch {0}'.format(config['DIRS']['CACHED_ADDR_FILE']))
            self.set()
        self.cache = open(config['DIRS']['CACHED_ADDR_FILE'], "r+")

    def get(self):
        """
        Get IP-address for domain from cache
        :return:
        """
        with open(config['DIRS']['CACHED_ADDR_FILE']) as cache:
            hosts = cache.read()
        if hosts:
            self.raw_cache = json.loads(hosts)
            return self.raw_cache.get(self.host)
        else:
            res = resolver.Resolver()
            res.nameservers = [config['DNS']['DNS1']]
            answers = res.query(self.host)
            l = [ip.address for ip in answers]
            self.raw_cache[self.host] = l
            return

    def set(self):
        """
        Update or create new record in cache
        :return:
        """
        tmp_filename = "{}.tmp".format(config['DIRS']['CACHED_ADDR_FILE'])
        ips = socket.gethostbyname_ex(self.host)[-1]
        self.raw_cache[self.host] = ips
        with open(tmp_filename, 'w+') as f:
            f.write(json.dumps(self.raw_cache, indent=2))
        shutil.move(tmp_filename, config['DIRS']['CACHED_ADDR_FILE'])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cache.close()


def init_logger():
    """
    Initiation logging system
    :return:
    """
    logging.basicConfig(format=u'[%(asctime)s] %(filename)s #%(levelname)-8s %(message)s', level=logging.ERROR,
                        datefmt='%Y-%m-%d %H:%M:%S')


def parse_args():
    """
    Analyze recieve args
    :return: dict
    """
    parser = argparse.ArgumentParser(description='Try to connect for url always')
    parser.add_argument("--url", nargs='?', default='', help="url or domain")
    parser.add_argument("-v", "--verbosity", action="count", help="Пояснять что будет сделано")
    args = parser.parse_args()
    if args.verbosity:
        if args.verbosity == 1:
            logging.getLogger().setLevel(logging.INFO)
        if args.verbosity > 1:
            logging.getLogger().setLevel(logging.DEBUG)
    return args


def main():
    init_logger()
    args = parse_args()
    domain = parse.urlparse(args.url)
    new_url = ''
    try:
        cache = Cache(domain.hostname)
        cache.set()
        new_url = args.url
    except socket.gaierror as e:
        logging.error(e)
        addr = cache.get()
        if not addr:
            logging.error('Can`t resolve domain and find IP in cache')
            new_url = args.url
        else:
            # TODO: get random ipaddr and convert to string
            new_url = domain._replace(netloc=''.join(addr)).geturl()
    finally:
        print(new_url)


if __name__ == '__main__':
    main()
