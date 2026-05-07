import os
import logging
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

AUTO_LOGIN_USER = os.environ.get('AUTO_LOGIN_USER', 'admin')
AUTO_LOGIN_PASS = os.environ.get('AUTO_LOGIN_PASS', 'admin')


class AutoLoginController(Home):

    @http.route('/web/login', type='http', auth='public', website=False, sitemap=False)
    def web_login(self, redirect_url='/odoo', **kw):
        if request.session.uid:
            return redirect(redirect_url, 302)

        db = request.db
        if db:
            try:
                uid = request.session.authenticate(db, AUTO_LOGIN_USER, AUTO_LOGIN_PASS)
                if uid:
                    request.uid = uid
                    _logger.debug("Auto-login: '%s' kullanıcısı otomatik giriş yaptı.", AUTO_LOGIN_USER)
                    return redirect(redirect_url, 302)
            except Exception:
                _logger.warning("Auto-login başarısız, giriş formu gösteriliyor.")

        return super().web_login(**kw)
