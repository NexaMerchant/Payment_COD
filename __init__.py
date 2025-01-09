# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo.api import Environment, SUPERUSER_ID
from odoo.sql_db import Cursor

from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(env):
    setup_provider(env, 'cod')


def uninstall_hook(env):
    reset_payment_provider(env, 'cod')


