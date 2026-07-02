from odoo import models, fields, api
from odoo.exceptions import UserError


class MuhasebeIslem(models.Model):
    _name = 'erp.muhasebe.islem'
    _description = 'Muhasebe İşlemi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tarih desc, name desc'

    name = fields.Char(string='İşlem No', readonly=True, default='Yeni')
    aciklama = fields.Char(string='Açıklama', required=True)
    tur = fields.Selection([
        ('gelir', 'Gelir'),
        ('gider', 'Gider'),
    ], string='İşlem Türü', required=True, tracking=True)
    kategori = fields.Selection([
        ('satis', 'Satış Geliri'),
        ('hizmet', 'Hizmet Geliri'),
        ('kira', 'Kira Geliri'),
        ('personel', 'Personel Gideri'),
        ('kira_gider', 'Kira Gideri'),
        ('malzeme', 'Malzeme/Hammadde'),
        ('elektrik_su', 'Elektrik/Su/Doğalgaz'),
        ('pazarlama', 'Pazarlama'),
        ('bakım', 'Bakım-Onarım'),
        ('vergi', 'Vergi/Harç'),
        ('diger', 'Diğer'),
    ], string='Kategori', required=True)
    tutar = fields.Float(string='Tutar (₺)', required=True, digits=(12, 2))
    tarih = fields.Date(string='Tarih', required=True, default=fields.Date.today)
    vade_tarihi = fields.Date(string='Vade Tarihi')
    sorumlu_id = fields.Many2one('res.users', string='Sorumlu',
                                  default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Müşteri/Tedarikçi')
    state = fields.Selection([
        ('taslak', 'Taslak'),
        ('onaylandi', 'Onaylandı'),
        ('odendi', 'Ödendi/Tahsil Edildi'),
        ('iptal', 'İptal'),
    ], string='Durum', default='taslak', tracking=True)
    referans = fields.Char(string='Referans No')
    notlar = fields.Text(string='Notlar')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Yeni') == 'Yeni':
                vals['name'] = self.env['ir.sequence'].next_by_code('erp.muhasebe.islem') or 'Yeni'
        return super().create(vals_list)

    def action_onayla(self):
        for rec in self:
            if rec.tutar <= 0:
                raise UserError('Tutar sıfırdan büyük olmalıdır.')
            rec.state = 'onaylandi'

    def action_odendi(self):
        for rec in self:
            rec.state = 'odendi'

    def action_iptal(self):
        for rec in self:
            if rec.state == 'odendi':
                raise UserError('Ödenmiş/tahsil edilmiş işlem iptal edilemez.')
            rec.state = 'iptal'

    def action_taslaga_al(self):
        for rec in self:
            rec.state = 'taslak'


class MuhasebeBütce(models.Model):
    _name = 'erp.muhasebe.butce'
    _description = 'Bütçe'
    _inherit = ['mail.thread']
    _order = 'yil desc, ay desc'

    name = fields.Char(string='Bütçe Adı', required=True)
    yil = fields.Integer(string='Yıl', required=True, default=lambda self: fields.Date.today().year)
    ay = fields.Selection([
        ('1', 'Ocak'), ('2', 'Şubat'), ('3', 'Mart'), ('4', 'Nisan'),
        ('5', 'Mayıs'), ('6', 'Haziran'), ('7', 'Temmuz'), ('8', 'Ağustos'),
        ('9', 'Eylül'), ('10', 'Ekim'), ('11', 'Kasım'), ('12', 'Aralık'),
    ], string='Ay', required=True)
    planlanan_gelir = fields.Float(string='Planlanan Gelir (₺)', digits=(12, 2))
    planlanan_gider = fields.Float(string='Planlanan Gider (₺)', digits=(12, 2))
    gerceklesen_gelir = fields.Float(string='Gerçekleşen Gelir (₺)',
                                      compute='_compute_gerceklesen', store=True, digits=(12, 2))
    gerceklesen_gider = fields.Float(string='Gerçekleşen Gider (₺)',
                                      compute='_compute_gerceklesen', store=True, digits=(12, 2))
    gelir_sapma = fields.Float(string='Gelir Sapması (₺)',
                                compute='_compute_sapmalar', store=True, digits=(12, 2))
    gider_sapma = fields.Float(string='Gider Sapması (₺)',
                                compute='_compute_sapmalar', store=True, digits=(12, 2))

    @api.depends('yil', 'ay')
    def _compute_gerceklesen(self):
        for rec in self:
            if not rec.yil or not rec.ay:
                rec.gerceklesen_gelir = 0.0
                rec.gerceklesen_gider = 0.0
                continue
            islemler = self.env['erp.muhasebe.islem'].search([
                ('state', '=', 'odendi'),
                ('tarih', '>=', f'{rec.yil}-{int(rec.ay):02d}-01'),
                ('tarih', '<=', f'{rec.yil}-{int(rec.ay):02d}-31'),
            ])
            rec.gerceklesen_gelir = sum(i.tutar for i in islemler if i.tur == 'gelir')
            rec.gerceklesen_gider = sum(i.tutar for i in islemler if i.tur == 'gider')

    @api.depends('planlanan_gelir', 'gerceklesen_gelir', 'planlanan_gider', 'gerceklesen_gider')
    def _compute_sapmalar(self):
        for rec in self:
            rec.gelir_sapma = rec.gerceklesen_gelir - rec.planlanan_gelir
            rec.gider_sapma = rec.gerceklesen_gider - rec.planlanan_gider
