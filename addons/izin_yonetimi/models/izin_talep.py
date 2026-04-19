from odoo import models, fields, api
from odoo.exceptions import UserError


class IzinTalep(models.Model):
    _name = 'izin.talep'
    _description = 'İzin Talebi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Talep No', readonly=True, default='Yeni')
    calisan_id = fields.Many2one('res.users', string='Çalışan', default=lambda self: self.env.user, required=True)
    izin_turu = fields.Selection([
        ('yillik', 'Yıllık İzin'),
        ('hastalik', 'Hastalık İzni'),
        ('mazeret', 'Mazeret İzni'),
        ('ucretsiz', 'Ücretsiz İzin'),
    ], string='İzin Türü', required=True)
    baslangic = fields.Date(string='Başlangıç Tarihi', required=True)
    bitis = fields.Date(string='Bitiş Tarihi', required=True)
    gun_sayisi = fields.Integer(string='Gün Sayısı', compute='_compute_gun_sayisi', store=True)
    aciklama = fields.Text(string='Açıklama')
    state = fields.Selection([
        ('taslak', 'Taslak'),
        ('beklemede', 'Onay Bekliyor'),
        ('onaylandi', 'Onaylandı'),
        ('reddedildi', 'Reddedildi'),
        ('iptal', 'İptal Edildi'),
    ], string='Durum', default='taslak', tracking=True)
    onaylayan_id = fields.Many2one('res.users', string='Onaylayan', readonly=True)
    red_nedeni = fields.Text(string='Red Nedeni', readonly=True)

    @api.depends('baslangic', 'bitis')
    def _compute_gun_sayisi(self):
        for rec in self:
            if rec.baslangic and rec.bitis:
                delta = rec.bitis - rec.baslangic
                rec.gun_sayisi = delta.days + 1
            else:
                rec.gun_sayisi = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('izin.talep') or 'Yeni'
        return super().create(vals_list)

    def action_gonder(self):
        for rec in self:
            if rec.baslangic > rec.bitis:
                raise UserError('Başlangıç tarihi bitiş tarihinden sonra olamaz.')
            rec.state = 'beklemede'

    def action_onayla(self):
        for rec in self:
            rec.state = 'onaylandi'
            rec.onaylayan_id = self.env.user

    def action_reddet(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'izin.red.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_talep_id': self.id},
        }

    def action_iptal(self):
        for rec in self:
            if rec.state == 'onaylandi':
                raise UserError('Onaylanmış izin iptal edilemez.')
            rec.state = 'iptal'


class IzinRedWizard(models.TransientModel):
    _name = 'izin.red.wizard'
    _description = 'İzin Red Sebebi'

    talep_id = fields.Many2one('izin.talep', required=True)
    red_nedeni = fields.Text(string='Red Nedeni', required=True)

    def action_reddet(self):
        self.talep_id.write({
            'state': 'reddedildi',
            'red_nedeni': self.red_nedeni,
            'onaylayan_id': self.env.user.id,
        })
