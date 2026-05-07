import os
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home


class AutoLoginController(Home):
    @http.route('/web/login', type='http', auth='none')
    def web_login(self, redirect=None, **kw):
        user = os.environ.get('AUTO_LOGIN_USER', '')
        password = os.environ.get('AUTO_LOGIN_PASS', '')
        if user and password and request.db:
            request.session.logout(keep_db=True)
            uid = request.session.authenticate(request.db, user, password)
            if uid:
                return request.redirect(self._login_redirect(uid, redirect=redirect))
        return super().web_login(redirect=redirect, **kw)