# import datetime
from odoo import _
from datetime import date
from dateutil import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HMSCancelAppointmentWizard(models.TransientModel):
    _name = 'hms.cancel.appointment.wizard'
    _description = 'Cancel appointment wizard'
    
    # @api.model
    # def default_get(self, fields):
    #     res = super(HMSCancelAppointmentWizard,self).default_get(fields)
    #     res['cancel_date'] = datetime.date.today()
    #     if self.env.context.get('active_id'):
    #         res['appointment_id'] = self.env.context.get('active_id')
    #     return res
    
    cancel_date = fields.Date(string='Cancel date',default=fields.Date.context_today,required=True)
    reason = fields.Text(string='Reason', required=True)
    appointment_id = fields.Many2one('hms.appointment',string="Appointment", required=True, domain=['|',('state','=','draft'),('state','=','create')])
    
    def cancel_appointment(self):
        passValidation = False
        errorMessage = "Error"
        cancel_appoinment_before_days = self.env['ir.config_parameter'].get_param("hospital_management_system.cancel_appoinment_before_days")
        
        for row in self.appointment_id:
            allow_date = self.appointment_id.booking_date + relativedelta.relativedelta(days=int(cancel_appoinment_before_days))
            number_of_days = abs((date.today() - self.appointment_id.booking_date).days)
            
            if  row.state == 'draft' or row.state == 'create':
                if int(number_of_days) < int(cancel_appoinment_before_days) :
                    passValidation = False
                    errorMessage = (_("Appoinment can not cancel as min allow date is %s .",allow_date))
                else:
                    passValidation = True  
            else:
                passValidation = False
                if row.state == 'done':
                    errorMessage = (_("Appoinment is  done."))
                elif row.state == 'cancel':
                    errorMessage = (_("Appoinment is canceled."))
                else:
                    errorMessage = (_("Only draft,create appoinment can be cancel."))
                
        if passValidation == True :
            self.appointment_id.write({'state': 'cancel'})
            return {
                'effect' : {
                    'fadeout' : 'slow',
                    'message' : 'Successfully canceled.',
                    'type' : 'rainbow_man',
                }
            }
            
            # return {
            #     'tag' : 'reload',
            #     'type' : 'ir.actions.client',
            # }
            
            # return {
            #     'type' : 'ir.actions.act_window',
            #     'view_mode' : 'form',
            #     'res_model' : 'hms.cancel.appointment.wizard',
            #     'target' : 'new',
            #     'res_id' : self.id,
            # }
        else:
            raise ValidationError(_(errorMessage))