#!/usr/bin/env python3

import argparse
import json
import logging
import random
import shutil
import os
from urllib import parse

from dns import resolver
from gevent import socket

DNS1 = "8.8.8.8"

cache_file = '{0}/try2connect.hosts'.format(os.path.expanduser('~'))


class Cache:
    """
    Class for working with cache records. Format 'domain': 'ip'
    """

    def __init__(self, host):
        self.host = host
        self.cache = open(cache_file, 'r+')
        self.raw_cache = json.load(self.cache)

    def fetch_ip_address(self):
        """
        Get IP-address for domain from cache
        :return:
        """
        if self.host in self.raw_cache:
            return self.raw_cache.get(self.host)
        else:
            #TODO: mv to push_host
            res = resolver.Resolver()
            res.nameservers = [DNS1]
            answers = res.query(self.host)
            ips = [ip.address for ip in answers]
            self.raw_cache[self.host] = ips
            self.cache = self.raw_cache
            return self.raw_cache[self.host]

    def push_host(self):
        """
        Update or create new record in cache
        :return:
        """
        tmp_file = '{}.tmp'.format(cache_file)
        ips = socket.gethostbyname_ex(self.host)[-1]
        self.raw_cache[self.host] = ips
        with open(tmp_file, 'w+') as f:
            f.write(json.dumps(self.raw_cache, indent=2))
        shutil.move(tmp_file, cache_file)

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


def prepare():
    """
    Create all env
    :return:
    """
    if not os.path.exists(cache_file):
        with open(cache_file, 'w+') as f:
            f.write('{}')


def main():
    prepare()
    init_logger()
    args = parse_args()
    domain = parse.urlparse(args.url)
    cache = Cache(domain.hostname)
    new_url = ''
    try:
        cache.push_host()
        new_url = args.url
    except socket.gaierror as e:
        logging.error(e)
        addr = cache.fetch_ip_address()
        if not addr:
            logging.error('Can`t resolve domain and find IP in cache')
            new_url = args.url
        else:
            ip = ''.join(random.choice(addr))
            new_url = domain._replace(netloc=ip).geturl()
    finally:
        print(new_url)


if __name__ == '__main__':
    main()
