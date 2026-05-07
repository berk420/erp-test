import os
import logging
from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)

AUTO_LOGIN_USER = os.environ.get('AUTO_LOGIN_USER', 'admin')
AUTO_LOGIN_PASS = os.environ.get('AUTO_LOGIN_PASS', 'admin')


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_user(cls):
        if not request.session.uid:
            db = request.db
            if db:
                try:
                    uid = request.session.authenticate(db, AUTO_LOGIN_USER, AUTO_LOGIN_PASS)
                    if uid:
                        request.uid = uid
                        _logger.debug("Auto-login: kullanıcı '%s' otomatik giriş yaptı.", AUTO_LOGIN_USER)
                        return
                except Exception:
                    _logger.warning("Auto-login başarısız, normal giriş ekranına yönlendiriliyor.")
        super()._auth_method_user()
