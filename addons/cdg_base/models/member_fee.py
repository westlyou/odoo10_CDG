# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging, time

_logger = logging.getLogger(__name__)


class MemberFee(models.Model):
    _name = 'member.fee'


    member_id = fields.Char(string='舊會員編號')
    member_note_id = fields.Char(string='會員名冊編號')
    adviser_id = fields.Char(string='舊顧問編號')
    year = fields.Char(string='年度')
    fee_id = fields.Char(string='收費編號')
    fee_payable = fields.Integer(string='應繳金額')
    fee_date = fields.Date(string='收費日期')
    clerk_id = fields.Char(string='收費員編號')
    worker_id = fields.Many2one(comodel_name='c.worker', string='輸入人員')
    db_chang_date = fields.Date(string='異動日期')
    fee_member = fields.Many2one(comodel_name='normal.p', string='關聯的捐款人')
    member_data_ids = fields.Many2one(comodel_name='member.data', string='關聯的轉檔資料')



    def data_input_form_DB(self):
        data = self.env['base.external.dbsource'].search([])
        lines = data.execute('SELECT * FROM 會員收費檔')
        i = 1
        for line in lines:
            _logger.error(' %s / %s', i, len(lines))
            self.create({
                'member_id': line[u'會員編號'],
                'member_note_id': line[u'會員名冊編號'],
                'year': line[u'年度'],
                'db_chang_date': self.check_db_date(line[u'異動日期']),
                'fee_payable': line[u'應繳金額'],
                'fee_date': self.check_db_date(line[u'收費日期']),
                'fee_id': line[u'收費編號'],
                'clerk_id': line[u'收費員編號'],
                'worker_id': self.check_user(line[u'輸入人員']),

            })
            i += 1



    def data_input_form_DB2(self):
        data = self.env['base.external.dbsource'].search([])
        lines = data.execute('SELECT * FROM 顧問收費檔')
        i = 1
        for line in lines:
            _logger.error(' %s / %s', i, len(lines))
            self.create({
                'adviser_id': line[u'顧問編號'],
                'year': line[u'年度'],
                'db_chang_date': self.check_db_date(line[u'異動日期']),
                'fee_payable': line[u'應繳金額'],
                'fee_date': self.check_db_date(line[u'收費日期']),
                'fee_id': line[u'收費編號'],
                'clerk_id': line[u'收費員編號'],
                'worker_id': self.check_user(line[u'輸入人員']),
            })
            i += 1


    def check_db_date(self, date):
        if date:
            try:
                time.strptime(date, "%Y-%m-%d")
                return date
            except:
                return None
        else:
            return None

    def check_user(self,row):
        check = self.env['c.worker'].search([('w_id','=',row)])
        if check.id > 0 :
            return check.id
        else:
            return None


