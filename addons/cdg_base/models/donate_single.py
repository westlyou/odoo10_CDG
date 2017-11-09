# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging, datetime
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DonateSingle(models.Model):
    _name = 'donate.single'

    # name = fields.Many2one(comodel_name='normal.p',string='姓名')

    paid_id = fields.Char(string='收費編號', readonly=True)
    donate_id = fields.Char(string='捐款編號', readonly=True)
    donate_member = fields.Many2one(comodel_name='normal.p', string='捐款者編號', domain=[('w_id', '!=', '')])  # demo用
    name = fields.Char(string='姓名', compute='set_donate_name')
    self_iden = fields.Char(string='身分證字號', compute='set_donate_name', store=True)
    cellphone = fields.Char(string='手機', compute='set_donate_name', store=True)
    con_phone = fields.Char(string='連絡電話', compute='set_donate_name', store=True)
    zip_code = fields.Char(string='郵遞區號', compute='set_donate_name', store=True)
    con_addr = fields.Char(string='聯絡地址', compute='set_donate_name', store=True)

    state = fields.Selection([(1, '已產生'), (2, '已作廢')],
                             string='狀態', default=1, index=True)

    donate_total = fields.Integer(string='捐款總額', compute='compute_total')

    receipt_send = fields.Boolean(string='收據寄送')
    report_send = fields.Boolean(string='報表寄送')
    year_receipt_send = fields.Boolean(string='年收據寄送')
    bridge = fields.Boolean(string='造橋')
    road = fields.Boolean(string='補路')
    coffin = fields.Boolean(string='施棺')
    poor_help = fields.Boolean(string='貧困扶助')
    bridge_money = fields.Integer(string='$')
    road_money = fields.Integer(string='$')
    coffin_money = fields.Integer(string='$')
    poor_help_money = fields.Integer(string='$')
    cash = fields.Boolean(string='現金')
    mail = fields.Boolean(string='郵政劃撥')
    credit_card = fields.Boolean(string='信用卡扣款')
    bank = fields.Boolean(string='銀行轉帳')
    person_check = fields.Many2many(comodel_name="normal.p", string="捐款人名冊", )
    family_check = fields.One2many(comodel_name='donate.family.line',inverse_name='parent_id', string='捐款人名冊')
    donate_list = fields.One2many(comodel_name='donate.order', inverse_name='donate_list_id', string='捐款明細')

    @api.model
    def create(self, vals):
        res_id = super(DonateSingle, self).create(vals)
        max = self.env['donate.order'].search([], order='paid_id desc', limit=1)
        donate_id = max.donate_id
        int_max = int(donate_id[1:]) + 1
        res_id.write({
            'donate_id': 'A' + str(int_max)
        })

        self.add_to_list_create(res_id)
        return res_id

    @api.onchange('bridge', 'road', 'coffin', 'poor_help')
    def set_default_price(self):
        if self.bridge and self.bridge_money == 0:
            self.bridge_money = 100
        elif self.bridge is False:
            self.bridge_money = 0
        if self.road and self.road_money == 0:
            self.road_money = 100
        elif self.road is False:
            self.road_money = 0
        if self.coffin and self.coffin_money == 0:
            self.coffin_money = 100
        elif self.coffin is False:
            self.coffin_money = 0
        if self.poor_help and self.poor_help_money == 0:
            self.poor_help_money = 100
        elif self.poor_help is False:
            self.poor_help_money = 0

    @api.onchange('bridge_money','road_money','coffin_money', 'poor_help_money')
    def set_checkbox_check(self):
        if self.bridge_money != 0:
            self.bridge = True
        else:
            self.bridge = False
        if self.road_money != 0:
            self.road = True
        else:
            self.road = False
        if self.coffin_money != 0:
            self.coffin = True
        else:
            self.coffin = False
        if self.poor_help_money != 0:
            self.poor_help = True
        else:
            self.poor_help = False

    @api.onchange('donate_member')
    def show_family(self):
        if self.donate_member.w_id != '' and self.donate_member.id > 0:
            member = self.env['normal.p'].search([('w_id', '=', self.donate_member.w_id)])
            r = []
            for line in member:
                r.append([0, 0, {
                    'donate_member': line.id
                }])
            self.update({
                'family_check': r
            })

    @api.depends('donate_list')
    def compute_total(self):
        for line in self:
            for row in line.donate_list:
                line.donate_total += row.donate

    def button_to_cnacel_donate(self):
        if self.state != 1:
            raise ValidationError(u'本捐款單已作廢!!')
        self.state = 2

    def add_to_list_create(self, record):

        max = self.env['donate.order'].search([], order='paid_id desc', limit=1)
        max_int = int(max.paid_id) + 1
        if record.family_check:
            for line in record.family_check:
                if record.bridge:
                    record.save_donate_list(1, str(max_int), line, record.bridge_money)
                    max_int = max_int + 1
                if record.road:
                    record.save_donate_list(2, str(max_int), line, record.road_money)
                    max_int = max_int + 1
                if record.coffin:
                    record.save_donate_list(3, str(max_int), line, record.coffin_money)
                    max_int = max_int + 1
                if record.poor_help:
                    record.save_donate_list(4, str(max_int), line, record.poor_help_money)
                    max_int = max_int + 1
        else:
            if record.bridge:
                record.save_donate_list(1, str(max_int), record.donate_member, record.bridge_money)
                max_int = max_int + 1
            if record.road:
                record.save_donate_list(2, str(max_int), record.donate_member, record.road_money)
                max_int = max_int + 1
            if record.coffin:
                record.save_donate_list(3, str(max_int), record.donate_member, record.coffin_money)
                max_int = max_int + 1
            if record.poor_help:
                record.save_donate_list(4, str(max_int), record.donate_member, record.poor_help_money)
                max_int = max_int + 1

    def add_to_list(self):
        # 將明細產生按鈕執行
        max = self.env['donate.order'].search([], order='paid_id desc', limit=1)
        max_int = int(max.paid_id) + 1
        if self.person_check:
            for line in self.person_check:
                if self.bridge:
                    self.save_donate_list(1, str(max_int), line, self.bridge_money)
                    max_int = max_int + 1
                if self.road:
                    self.save_donate_list(2, str(max_int), line, self.road_money)
                    max_int = max_int + 1
                if self.coffin:
                    self.save_donate_list(3, str(max_int), line, self.coffin_money)
                    max_int = max_int + 1
                if self.poor_help:
                    self.save_donate_list(4, str(max_int), line, self.poor_help_money)
                    max_int = max_int + 1
        else:
            if self.bridge:
                self.save_donate_list(1, str(max_int), self.donate_member, self.bridge_money)
                max_int = max_int + 1
            if self.road:
                self.save_donate_list(2, str(max_int), self.donate_member, self.road_money)
                max_int = max_int + 1
            if self.coffin:
                self.save_donate_list(3, str(max_int), self.donate_member, self.coffin_money)
                max_int = max_int + 1
            if self.poor_help:
                self.save_donate_list(4, str(max_int), self.donate_member, self.poor_help_money)
                max_int = max_int + 1

    def save_donate_list(self, donate_type, paid_id, member_id, money):  # 將明細產生
        self.write({
            'donate_list': [(0, 0, {
                'donate_id': self.donate_id,
                'paid_id': str(paid_id),
                'donate_member': member_id.donate_member.id,
                'donate_type': donate_type,
                'donate': money,
                'donate_date': datetime.date.today(),
                'self_id': member_id.donate_member.self_iden,
            })]
        })



    def parent_list_creat(self):
        self.person_check = self.donate_member.mapped('donate_family1')

    @api.depends('donate_member')
    def set_donate_name(self):
        for line in self:
            normal_p = line.donate_member
            line.name = normal_p.name
            line.cellpnone = normal_p.cellphone
            line.con_phone = normal_p.con_phone
            line.self_iden = normal_p.self_iden
            line.zip_code = normal_p.zip_code
            line.con_addr = normal_p.con_addr


class DonateSingleLine(models.Model):
    _name = 'donate.family.line'

    parent_id = fields.Many2one(comodel_name='donate.single')
    family_new_coding = fields.Char(string='捐款者編號',related='donate_member.new_coding', readonly=True)
    donate_member = fields.Many2one(comodel_name='normal.p', string='捐款人')
