from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale order for hospital management system'
    
    confirmed_user_id = fields.Many2one('res.users',string="Confirmed user")
    
    def action_confirm(self):
        super(SaleOrder,self).action_confirm()
        if not self.confirmed_user_id :
            self.confirmed_user_id = self.env.user.id
            
    def _prepare_invoice(self):
        invoice_values = super(SaleOrder,self)._prepare_invoice()
        invoice_values['so_confirmed_user_id'] = self.confirmed_user_id.id
        return invoice_values

