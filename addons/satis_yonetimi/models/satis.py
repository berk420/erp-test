from odoo import models, fields, api
from odoo.exceptions import UserError


class SatisSiparis(models.Model):
    _name = 'erp.satis.siparis'
    _description = 'Satış Siparişi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'siparis_tarihi desc, name desc'

    name = fields.Char(string='Sipariş No', readonly=True, default='Yeni')
    musteri_id = fields.Many2one('res.partner', string='Müşteri', required=True)
    satis_temsilcisi = fields.Many2one('res.users', string='Satış Temsilcisi',
                                        default=lambda self: self.env.user)
    siparis_tarihi = fields.Date(string='Sipariş Tarihi', required=True,
                                  default=fields.Date.today)
    teslim_tarihi = fields.Date(string='Teslim Tarihi')
    state = fields.Selection([
        ('teklif', 'Teklif'),
        ('onaylandi', 'Onaylandı'),
        ('sevk', 'Sevk Edildi'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal'),
    ], string='Durum', default='teklif', tracking=True)
    kalem_ids = fields.One2many('erp.satis.kalem', 'siparis_id', string='Sipariş Kalemleri')
    ara_toplam = fields.Float(string='Ara Toplam', compute='_compute_tutarlar',
                               store=True, digits=(12, 2))
    kdv_tutari = fields.Float(string='KDV Tutarı', compute='_compute_tutarlar',
                               store=True, digits=(12, 2))
    genel_toplam = fields.Float(string='Genel Toplam', compute='_compute_tutarlar',
                                 store=True, digits=(12, 2))
    bolge = fields.Selection([
        ('marmara', 'Marmara'),
        ('ege', 'Ege'),
        ('akdeniz', 'Akdeniz'),
        ('ic_anadolu', 'İç Anadolu'),
        ('karadeniz', 'Karadeniz'),
        ('dogu', 'Doğu Anadolu'),
        ('guneydogu', 'Güneydoğu'),
    ], string='Bölge')
    kategori = fields.Selection([
        ('elektronik', 'Elektronik'),
        ('gida', 'Gıda'),
        ('tekstil', 'Tekstil'),
        ('mobilya', 'Mobilya'),
        ('otomotiv', 'Otomotiv'),
    ], string='Kategori')
    notlar = fields.Text(string='Notlar')

    @api.depends('kalem_ids.toplam', 'kalem_ids.kdv')
    def _compute_tutarlar(self):
        for rec in self:
            rec.ara_toplam = sum(rec.kalem_ids.mapped('toplam'))
            rec.kdv_tutari = sum(rec.kalem_ids.mapped('kdv'))
            rec.genel_toplam = rec.ara_toplam + rec.kdv_tutari

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Yeni') == 'Yeni':
                vals['name'] = self.env['ir.sequence'].next_by_code('erp.satis.siparis') or 'Yeni'
        return super().create(vals_list)

    def action_onayla(self):
        for rec in self:
            if not rec.kalem_ids:
                raise UserError('Siparişte en az bir kalem bulunmalıdır.')
            rec.state = 'onaylandi'

    def action_sevk(self):
        for rec in self:
            rec.state = 'sevk'

    def action_tamamla(self):
        for rec in self:
            rec.state = 'tamamlandi'

    def action_iptal(self):
        for rec in self:
            if rec.state == 'tamamlandi':
                raise UserError('Tamamlanmış sipariş iptal edilemez.')
            rec.state = 'iptal'

    def action_taslaga_al(self):
        for rec in self:
            rec.state = 'teklif'


class SatisKalem(models.Model):
    _name = 'erp.satis.kalem'
    _description = 'Satış Sipariş Kalemi'

    siparis_id = fields.Many2one('erp.satis.siparis', string='Sipariş',
                                  ondelete='cascade', required=True)
    urun_adi = fields.Char(string='Ürün', required=True)
    aciklama = fields.Char(string='Açıklama')
    miktar = fields.Float(string='Miktar', default=1.0)
    birim = fields.Selection([
        ('adet', 'Adet'),
        ('kg', 'Kg'),
        ('lt', 'Lt'),
        ('m', 'Metre'),
        ('kutu', 'Kutu'),
    ], string='Birim', default='adet')
    birim_fiyat = fields.Float(string='Birim Fiyat (₺)', digits=(12, 2))
    kdv_orani = fields.Selection([
        ('0', '%0'),
        ('8', '%8'),
        ('10', '%10'),
        ('18', '%18'),
        ('20', '%20'),
    ], string='KDV Oranı', default='20')
    toplam = fields.Float(string='Toplam', compute='_compute_toplam',
                           store=True, digits=(12, 2))
    kdv = fields.Float(string='KDV', compute='_compute_toplam',
                        store=True, digits=(12, 2))

    @api.depends('miktar', 'birim_fiyat', 'kdv_orani')
    def _compute_toplam(self):
        for rec in self:
            rec.toplam = rec.miktar * rec.birim_fiyat
            rec.kdv = rec.toplam * (int(rec.kdv_orani or 0) / 100)
