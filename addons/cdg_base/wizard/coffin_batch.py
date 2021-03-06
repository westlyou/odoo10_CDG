# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class coffinbatch(models.Model):
    _name = 'coffin.batch'
    _description = u'施棺批次處理'

    flag = fields.Boolean(default=False ,string="確認進行批次處理?")
    coffin_data_lists = fields.Many2many(comodel_name='coffin.base')

    def confirm_to_batch(self):
        if self.flag == True:
            for data in self.coffin_data_lists:
                default_price_flag = False  # 判斷是否為基本設定檔的施棺滿足額
                temp_default_price = 0  # 暫存用的, 沒幹嘛
                big_donate_flag = False
                basic_setting = self.env['ir.config_parameter'].search([])
                if data.donate_apply_price == 0 and data.exception_case == False:  # 如果申請金額沒有填入特定的施棺滿足額, 則自動預設為基本設定檔的施棺滿足額
                    for line in basic_setting:  # 讀取基本設定檔的施棺滿足額
                        if line.key == 'coffin_amount':
                            data.donate_apply_price = int(line.value)
                            default_price_flag = True
                elif data.donate_apply_price != 0 and data.exception_case == False:
                    for line in basic_setting:  # 讀取基本設定檔的施棺滿足額
                        if line.key == 'coffin_amount':
                            data.donate_apply_price = int(line.value)
                            default_price_flag = True
                else:  # 如果有輸入申請金額, 則還是要讀取基本設定檔的施棺滿足額, 後續程式要判斷用
                    for line in basic_setting:  # 讀取基本設定檔的施棺滿足額
                        if line.key == 'coffin_amount':
                            temp_default_price = int(line.value)
                            default_price_flag = False

                for line in data.batch_donate:  # 從捐助資料表中, 計算目前的累積金額
                    data.donate_price = int(float(data.donate_price)) + int(float(line.donate_price))

                Cumulative_amount = data.donate_apply_price - int(float(data.donate_price))  # 計算已累積金額與施棺滿足額的差額
                flag = False  # 後續程式判讀使否結案用

                if Cumulative_amount == 0:  # 初始判斷累積金額是否已滿足施棺滿足額
                    data.finish = True
                    flag = True

                if data.finish == True:  # 判斷該專案是否已結案
                    raise ValidationError(u'已結案，無法再更改')
                elif data.finish == False:
                    lines = self.env['donate.order'].search([('donate_type', '=', 3),('available_balance', '<', 5000), ('use_amount', '=', False),('donate_date', '<', data.coffin_date)])
                    if lines and flag == False:
                        for line in lines:
                            if Cumulative_amount == 0:  # 達到施棺滿足額
                                data.finish = True
                                flag = True
                                break
                            if int(line.available_balance) == temp_default_price and line.donate_type == 3:  # 過濾單筆施棺捐款為3萬元的資料, 保險用的
                                continue
                            elif int(line.available_balance) <= Cumulative_amount and flag == False:  # 判斷 目前的施棺捐款額是否小於等於施棺滿足額
                                data.write({
                                    'batch_donate': [(0, 0, {
                                        'donate_order_id': line.id,
                                        'history_donate_records':line.available_balance
                                    })]
                                })
                                line.use_amount = True  # 確認已支用此筆施棺捐款金額
                                line.used_money = line.used_money + line.available_balance  # 已用金額
                                data.donate_price = int(float(data.donate_price)) + line.available_balance  # 將捐款金額加入累積金額
                                Cumulative_amount = Cumulative_amount - line.available_balance  # 施棺滿足額 減掉 捐款額
                                line.available_balance = 0  # 該筆捐款金額歸 0
                            elif int(line.available_balance) > Cumulative_amount and flag == False:  # 單筆捐款大於施棺滿足額的差額
                                data.write({
                                    'batch_donate': [(0, 0, {
                                        'donate_order_id': line.id,
                                        'history_donate_records': line.available_balance - (line.available_balance - Cumulative_amount)
                                    })]
                                })
                                line.used_money = line.used_money + line.available_balance - (line.available_balance - Cumulative_amount)  # 已用金額
                                line.available_balance = line.available_balance - Cumulative_amount  # 捐款金額減掉施棺滿足額的差額, 再把餘額寫回可用餘額之中
                                data.donate_price = int(float(data.donate_price)) + Cumulative_amount
                                Cumulative_amount = 0  # 達到施棺滿足額, 所以差額歸0
                                line.use_amount = False
                if Cumulative_amount != 0:
                    raise ValidationError(u'無法湊足施棺滿足額')
        elif self.flag == False:
            raise ValidationError(u'未確認是否進行批次處理，請勾選上方 [ 確認進行批次處理? ] 之選項')
        return True;
