#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time


sys.path.append(os.path.abspath(os.path.join(__file__,'../../../')))

import tele
from tele.tools import config, topological_sort, unique
from tele.netsvc import init_logger
from tele.tests import standalone_tests
import tele.tests.loader

_logger = logging.getLogger('tele.tests.test_module_operations')

BLACKLIST = {
    'auth_ldap', 'document_ftp', 'website_instantclick', 'pad',
    'pad_project', 'note_pad', 'pos_cache', 'pos_blackbox_be', 'payment_test',
}
IGNORE = ('hw_', 'theme_', 'l10n_', 'test_', 'payment_')


def install(db_name, module_id, module_name):
    with tele.registry(db_name).cursor() as cr:
        env = tele.api.Environment(cr, tele.SUPERUSER_ID, {})
        module = env['ir.module.module'].browse(module_id)
        module.button_immediate_install()
    _logger.info('%s installed', module_name)


def uninstall(db_name, module_id, module_name):
    with tele.registry(db_name).cursor() as cr:
        env = tele.api.Environment(cr, tele.SUPERUSER_ID, {})
        module = env['ir.module.module'].browse(module_id)
        module.button_immediate_uninstall()
    _logger.info('%s uninstalled', module_name)


def cycle(db_name, module_id, module_name):
    install(db_name, module_id, module_name)
    uninstall(db_name, module_id, module_name)
    install(db_name, module_id, module_name)


class CheckAddons(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        self.values = namespace
        config._check_applets_path(self, option_string, values, self)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Script for testing the install / uninstall / reinstall cycle of Tele modules")
    parser.add_argument("--database", "-d", type=str, required=True,
        help="The database to test (note: must have only 'base' installed)")
    parser.add_argument("--data-dir", "-D", dest="data_dir", type=str,
        help="Directory where to store Tele data"
    )
    parser.add_argument("--skip", "-s", type=str,
        help="Comma-separated list of modules to skip (they will only be installed)")
    parser.add_argument("--resume-at", "-r", type=str,
        help="Skip modules (only install) up to the specified one in topological order")
    parser.add_argument("--applets-path", "-p", type=str, action=CheckAddons,
        help="Comma-separated list of paths to directories containing extra Tele modules")
    parser.add_argument("--uninstall", "-U", type=str,
        help="Comma-separated list of modules to uninstall/reinstall")
    parser.add_argument("--standalone", type=str,
        help="Launch standalone scripts tagged with @standalone. Accepts a list of "
             "module names or tags separated by commas. 'all' will run all available scripts."
    )
    return parser.parse_args()


def test_full(args):
    """ Test full install/uninstall/reinstall cycle for all modules """
    with tele.registry(args.database).cursor() as cr:
        env = tele.api.Environment(cr, tele.SUPERUSER_ID, {})

        def valid(module):
            return not (
                module.name in BLACKLIST
                or module.name.startswith(IGNORE)
                or module.state in ('installed', 'uninstallable')
            )

        modules = env['ir.module.module'].search([]).filtered(valid)

        # order modules in topological order
        modules = modules.browse(topological_sort({
            module.id: module.dependencies_id.depend_id.ids
            for module in modules
        }))
        modules_todo = [(module.id, module.name) for module in modules]

    resume = args.resume_at
    skip = set(args.skip.split(',')) if args.skip else set()
    for module_id, module_name in modules_todo:
        if module_name == resume:
            resume = None

        if resume or module_name in skip:
            install(args.database, module_id, module_name)
        else:
            cycle(args.database, module_id, module_name)


def test_uninstall(args):
    """ Tries to uninstall/reinstall one ore more modules"""
    domain = [('name', 'in', args.uninstall.split(',')), ('state', '=', 'installed')]
    with tele.registry(args.database).cursor() as cr:
        env = tele.api.Environment(cr, tele.SUPERUSER_ID, {})
        modules = env['ir.module.module'].search(domain)
        modules_todo = [(module.id, module.name) for module in modules]

    for module_id, module_name in modules_todo:
        uninstall(args.database, module_id, module_name)
        install(args.database, module_id, module_name)


def test_scripts(args):
    """ Tries to launch standalone scripts tagged with @post_testing """
    # load the registry once for script discovery
    registry = tele.registry(args.database)
    for module_name in registry._init_modules:
        # import tests for loaded modules
        tele.tests.loader.get_test_modules(module_name)

    # fetch and filter scripts to test
    funcs = list(unique(
        func
        for tag in args.standalone.split(',')
        for func in standalone_tests[tag]
    ))

    start_time = time.time()
    for index, func in enumerate(funcs, start=1):
        with tele.registry(args.database).cursor() as cr:
            env = tele.api.Environment(cr, tele.SUPERUSER_ID, {})
            _logger.info("Executing standalone script: %s (%d / %d)",
                         func.__name__, index, len(funcs))
            try:
                func(env)
            except Exception:
                _logger.error("Standalone script %s failed", func.__name__, exc_info=True)

    _logger.info("%d standalone scripts executed in %.2fs" % (len(funcs), time.time() - start_time))


if __name__ == '__main__':
    args = parse_args()

    # handle paths option
    if args.applets_path:
        tele.tools.config['applets_path'] = ','.join([args.applets_path, tele.tools.config['applets_path']])
        if args.data_dir:
            tele.tools.config['data_dir'] = args.data_dir
        tele.modules.module.initialize_sys_path()

    init_logger()
    logging.getLogger('tele.modules.loading').setLevel(logging.CRITICAL)
    logging.getLogger('tele.sql_db').setLevel(logging.CRITICAL)

    try:
        if args.uninstall:
            test_uninstall(args)
        elif args.standalone:
            test_scripts(args)
        else:
            test_full(args)
    except Exception as e:
        _logger.exception("An error occured during standalone tests: %s", e)
