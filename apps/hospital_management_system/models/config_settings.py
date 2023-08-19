from odoo import fields, models

class ConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    cancel_appoinment_before_days = fields.Integer(string='Cancel appoinment before days', default=0, config_parameter="hospital_management_system.cancel_appoinment_before_days")
