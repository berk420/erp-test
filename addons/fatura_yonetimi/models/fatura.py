from odoo import models, fields, api
from odoo.exceptions import UserError


class Fatura(models.Model):
    _name = 'erp.fatura'
    _description = 'ERP Fatura'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fatura_tarihi desc, name desc'

    name = fields.Char(string='Fatura No', readonly=True, default='Yeni')
    musteri_id = fields.Many2one('res.partner', string='Müşteri / Firma', required=True)
    fatura_tarihi = fields.Date(string='Fatura Tarihi', required=True, default=fields.Date.today)
    vade_tarihi = fields.Date(string='Vade Tarihi', required=True)
    state = fields.Selection([
        ('taslak', 'Taslak'),
        ('onaylandi', 'Onaylandı'),
        ('odendi', 'Ödendi'),
        ('iptal', 'İptal'),
    ], string='Durum', default='taslak', tracking=True)
    kalem_ids = fields.One2many('erp.fatura.kalemi', 'fatura_id', string='Fatura Kalemleri')
    ara_toplam = fields.Float(
        string='Ara Toplam (KDV Hariç)',
        compute='_compute_tutarlar', store=True, digits=(12, 2))
    vergi_tutari = fields.Float(
        string='KDV Tutarı',
        compute='_compute_tutarlar', store=True, digits=(12, 2))
    genel_toplam = fields.Float(
        string='Genel Toplam (KDV Dahil)',
        compute='_compute_tutarlar', store=True, digits=(12, 2))
    notlar = fields.Text(string='Notlar')
    odeme_tarihi = fields.Date(string='Ödeme Tarihi', readonly=True)

    @api.depends('kalem_ids.ara_toplam', 'kalem_ids.kdv_tutari')
    def _compute_tutarlar(self):
        for rec in self:
            rec.ara_toplam = sum(rec.kalem_ids.mapped('ara_toplam'))
            rec.vergi_tutari = sum(rec.kalem_ids.mapped('kdv_tutari'))
            rec.genel_toplam = rec.ara_toplam + rec.vergi_tutari

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Yeni') == 'Yeni':
                vals['name'] = self.env['ir.sequence'].next_by_code('erp.fatura') or 'Yeni'
        return super().create(vals_list)

    def action_onayla(self):
        for rec in self:
            if not rec.kalem_ids:
                raise UserError('Faturada en az bir kalem bulunmalıdır.')
            rec.state = 'onaylandi'

    def action_odendi(self):
        for rec in self:
            if rec.state != 'onaylandi':
                raise UserError('Sadece onaylanmış faturalar ödenebilir.')
            rec.state = 'odendi'
            rec.odeme_tarihi = fields.Date.today()

    def action_iptal(self):
        for rec in self:
            if rec.state == 'odendi':
                raise UserError('Ödenmiş fatura iptal edilemez.')
            rec.state = 'iptal'

    def action_taslaga_al(self):
        for rec in self:
            if rec.state != 'iptal':
                raise UserError('Sadece iptal edilmiş faturalar taslağa alınabilir.')
            rec.state = 'taslak'


class FaturaKalemi(models.Model):
    _name = 'erp.fatura.kalemi'
    _description = 'Fatura Kalemi'

    fatura_id = fields.Many2one('erp.fatura', string='Fatura', ondelete='cascade', required=True)
    urun_adi = fields.Char(string='Ürün / Hizmet', required=True)
    aciklama = fields.Char(string='Açıklama')
    miktar = fields.Float(string='Miktar', default=1.0)
    birim_fiyat = fields.Float(string='Birim Fiyat (₺)', digits=(12, 2))
    kdv_orani = fields.Selection([
        ('0', '%0'),
        ('8', '%8'),
        ('10', '%10'),
        ('18', '%18'),
        ('20', '%20'),
    ], string='KDV', default='20')
    ara_toplam = fields.Float(
        string='Ara Toplam', compute='_compute_ara_toplam', store=True, digits=(12, 2))
    kdv_tutari = fields.Float(
        string='KDV', compute='_compute_ara_toplam', store=True, digits=(12, 2))

    @api.depends('miktar', 'birim_fiyat', 'kdv_orani')
    def _compute_ara_toplam(self):
        for rec in self:
            rec.ara_toplam = rec.miktar * rec.birim_fiyat
            rec.kdv_tutari = rec.ara_toplam * (int(rec.kdv_orani or 0) / 100)
