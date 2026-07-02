from odoo import models, fields, api
from odoo.exceptions import UserError


class StokUrun(models.Model):
    _name = 'erp.stok.urun'
    _description = 'Stok Ürünü'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Ürün Adı', required=True, tracking=True)
    kod = fields.Char(string='Ürün Kodu', required=True)
    kategori = fields.Selection([
        ('hammadde', 'Hammadde'),
        ('yari_mamul', 'Yarı Mamul'),
        ('mamul', 'Mamul'),
        ('sarf', 'Sarf Malzeme'),
        ('diger', 'Diğer'),
    ], string='Kategori', default='mamul', required=True)
    birim = fields.Selection([
        ('adet', 'Adet'),
        ('kg', 'Kg'),
        ('lt', 'Lt'),
        ('m', 'Metre'),
        ('kutu', 'Kutu'),
        ('palet', 'Palet'),
    ], string='Birim', default='adet', required=True)
    birim_maliyet = fields.Float(string='Birim Maliyet (₺)', digits=(12, 2))
    kritik_stok = fields.Float(string='Kritik Stok Seviyesi', default=0.0)
    mevcut_stok = fields.Float(string='Mevcut Stok', compute='_compute_stok', store=True)
    hareket_ids = fields.One2many('erp.stok.hareket', 'urun_id', string='Stok Hareketleri')
    aktif = fields.Boolean(string='Aktif', default=True)
    notlar = fields.Text(string='Notlar')

    @api.depends('hareket_ids.miktar', 'hareket_ids.tur', 'hareket_ids.state')
    def _compute_stok(self):
        for rec in self:
            giris = sum(
                h.miktar for h in rec.hareket_ids
                if h.tur == 'giris' and h.state == 'tamamlandi'
            )
            cikis = sum(
                h.miktar for h in rec.hareket_ids
                if h.tur == 'cikis' and h.state == 'tamamlandi'
            )
            rec.mevcut_stok = giris - cikis

    def stok_uyari_var_mi(self):
        self.ensure_one()
        return self.mevcut_stok <= self.kritik_stok


class StokHareket(models.Model):
    _name = 'erp.stok.hareket'
    _description = 'Stok Hareketi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tarih desc, name desc'

    name = fields.Char(string='Hareket No', readonly=True, default='Yeni')
    urun_id = fields.Many2one('erp.stok.urun', string='Ürün', required=True)
    tur = fields.Selection([
        ('giris', 'Stok Girişi'),
        ('cikis', 'Stok Çıkışı'),
        ('transfer', 'Transfer'),
        ('sayim', 'Sayım Düzeltme'),
    ], string='Hareket Türü', required=True, default='giris', tracking=True)
    miktar = fields.Float(string='Miktar', required=True, default=1.0)
    tarih = fields.Date(string='Tarih', required=True, default=fields.Date.today)
    sorumlu_id = fields.Many2one('res.users', string='Sorumlu',
                                  default=lambda self: self.env.user)
    kaynak = fields.Char(string='Kaynak/Referans')
    state = fields.Selection([
        ('taslak', 'Taslak'),
        ('onaylandi', 'Onaylandı'),
        ('tamamlandi', 'Tamamlandı'),
        ('iptal', 'İptal'),
    ], string='Durum', default='taslak', tracking=True)
    notlar = fields.Text(string='Notlar')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Yeni') == 'Yeni':
                vals['name'] = self.env['ir.sequence'].next_by_code('erp.stok.hareket') or 'Yeni'
        return super().create(vals_list)

    def action_onayla(self):
        for rec in self:
            if rec.miktar <= 0:
                raise UserError('Miktar sıfırdan büyük olmalıdır.')
            rec.state = 'onaylandi'

    def action_tamamla(self):
        for rec in self:
            if rec.tur == 'cikis':
                if rec.urun_id.mevcut_stok < rec.miktar:
                    raise UserError(
                        f'Yetersiz stok! Mevcut: {rec.urun_id.mevcut_stok} '
                        f'{rec.urun_id.birim}, İstenen: {rec.miktar} {rec.urun_id.birim}'
                    )
            rec.state = 'tamamlandi'

    def action_iptal(self):
        for rec in self:
            if rec.state == 'tamamlandi':
                raise UserError('Tamamlanmış hareket iptal edilemez.')
            rec.state = 'iptal'

    def action_taslaga_al(self):
        for rec in self:
            rec.state = 'taslak'
