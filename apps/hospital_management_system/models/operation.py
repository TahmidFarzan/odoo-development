from odoo import _
from odoo import api, fields, models

class HMSOperation(models.Model):
    _name = 'hms.operation'
    _description = 'Operation for hospital management system'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    _log_access=False
    _order='sequence,id'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    doctor_id = fields.Many2one('hms.doctor',string="Doctor", tracking=True, ondelete="restrict" )
    reference_record = fields.Reference(selection=[('hms.patient','Patient'),('hms.appointment','Appointment')],string="Reference record",)
    sequence = fields.Integer(string="sequence", default="1")
    
    @api.model
    def name_create(self, name):
        return self.create({'name':name}).name_get()[0]
    
    
