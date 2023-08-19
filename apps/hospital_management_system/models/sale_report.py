from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleReport(models.Model):
    _inherit = 'sale.report'
    _description = 'Sale order for hospital management system'
    
    confirmed_user_id = fields.Many2one('res.users',string="Confirmed user",readonly=True)
    
    def _select_additional_fields(self, fields):
        fields['confirmed_user_id'] = ", s.confirmed_user_id"
        return super(SaleReport,self)._select_additional_fields(fields)


