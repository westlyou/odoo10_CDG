# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CoffinBase(models.Model):
    _name = 'coffin.base'

    name = fields.Char()
    coffin_id = fields.Char(string="施棺編號")
    donate_type = fields.Selection(selection=[('Z','零捐'),('A','累積')],string='捐助方式')
    coffin_date = fields.Date(string='施棺日期')
    coffin_date_year = fields.Char(string='年度')
    coffin_date_group = fields.Char(string='期別')
    user = fields.Char(string='受施者')
    geter = fields.Char(string='領款人')
    dealer = fields.Char(string='處理者')
    con_phone = fields.Char(string='聯絡電話(一)')
    con_phone2 = fields.Char(string='聯絡電話(二)')
    cellphone = fields.Char(string='手機')
    zip_code = fields.Char(string='郵遞區號')
    con_addr = fields.Char(string='通訊地址')
    donater_ps = fields.Text(string='捐款者備註')
    ps = fields.Text(string='備註')
    donate_price = fields.Char(string='累積金額',store=True)
    finish = fields.Boolean(string='是否結案')
    batch_donate = fields.One2many(comodel_name='coffin.donation',inverse_name='coffin_donation_id',string='捐助資料')
    create_date = fields.Date(string='建檔日期')

    def add_coffin_file(self):
        lines = self.env['donate.order'].search([('donate_id', '!=', ''), ('donate', '!=', 0),('donate_type', '=', '03')])
        #lines = self.env['donate.order'].search([('donate_id', '!=', ''), ('donate', '!=', 0), ('donate_type', '=', '03'), ('state', '=', 1),('used_amount', '!=', 'donate')])
        basic_setting = self.env['ir.config_parameter'].search([])
        coffin_amount = 0
        for line in basic_setting:
            if line.key == 'coffin_amount':
                coffin_amount = int(line.value)

        Cumulative_amount = 30000 - int(self.donate_price)
        flag = False
        for line in lines:
            if int(self.donate_price) == Cumulative_amount:
                flag = True

            if (int(self.donate_price) + int(line.donate)) <= Cumulative_amount and flag == False:
                self.write({
                    'batch_donate': [(0, 0, {
                        'donate_id': line.donate_id,
                        'donate_price': line.donate,
                        'coffin_id': self.coffin_id,
                    })]
                })
                self.donate_price = int(self.donate_price) + line.donate
                #line.used_amount = line.donate

            if (int(self.donate_price) + int(line.donate)) > Cumulative_amount and flag == False:
                difference = (int(self.donate_price) + int(line.donate)) - Cumulative_amount
                self.donate_price = int(self.donate_price) + (line.donate - difference)
                donate_difference = line.donate - difference
                self.write({
                    'batch_donate': [(0, 0, {
                        'donate_id': line.donate_id,
                        'donate_price': donate_difference,
                        'coffin_id': self.coffin_id
                    })]
                })
                #line.used_amount = line.donate_difference
                flag = True
        return True;

    #@api.depends('batch_donate')
    def compute_total(self):
        for line in self:
            for row in line.batch_donate:
                line.donate_price = int(line.donate_price) + int(row.donate_price)

    def data_input_coffin(self):
        data = self.env['base.external.dbsource'].search([])
        lines = data.execute('SELECT * FROM 施棺檔')
        for line in lines:
            id_create2 = self.create({
                'coffin_id': line[u'施棺編號'],
                'donate_type': line[u'捐助方式'],
                'user': line[u'受施者'],
                'con_phone': line[u'電話一'],
                'con_phone2':line[u'電話二'],
                'cellphone':line[u'手機'],
                'geter': line[u'領款人'],
                'dealer':line[u'處理者'],
                'zip_code':line[u'郵遞區號'],
                'con_addr':line[u'通訊地址'],
                'coffin_date':self.check(line[u'施棺日期']),
                'create_date':self.check(line[u'建檔日期']),
                'db_chang_date':self.check(line[u'異動日期']),
                'finish':self.checkbool(line[u'結案']),
                'donate_price':line[u'已捐總額'],
                'coffin_date_year':line[u'年度'],
                'coffin_date_group':line[u'期別'],
            })

    def check_db_date(self, date):
        if date:
            try:
                time.strptime(date, "%Y-%m-%d")
                return date
            except:
                return None
        else:
            return None
    def checkbool(self,bool):
        if bool == 'Y':
            return True
        elif bool == 'N':
            return False

    def check(self,date_check):
        if date_check:
            return date_check
        else:
            return None

