import random
from odoo import _
from datetime import date
from dateutil import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HMSAppointment(models.Model):
    _name = 'hms.appointment'
    _description = 'Appointment for hospital management system'
    
    _inherit = ['mail.thread','mail.activity.mixin']
    
    _rec_name = 'reference'
    # _log_access=False
    _order= 'id desc'
    
    name = fields.Char(string='Name', required=True, tracking=1)
    capitalize_name = fields.Char(string='Capitalize name', tracking=True, compute="_compute_capitalize_name")
    note = fields.Text(string='Note', required=False, tracking=True)
    reference = fields.Char(string='Reference', default=lambda self : _("New"))
    doctor_id = fields.Many2one('hms.doctor',string="Doctor", required=True, tracking=True, ondelete="restrict" )
    patient_id = fields.Many2one('hms.patient',string="Patient", required=True, tracking=True, ondelete="cascade" )
    operation_id = fields.Many2one('hms.operation',string="Operation", tracking=True, ondelete="restrict" )
    appointment_time = fields.Datetime(string='Appointment time', required=True, tracking=True, default=fields.Datetime.now)
    booking_date = fields.Date(string='Booking date', required=True, tracking=True, default=fields.Date.context_today, readonly=True)
    prescription = fields.Html(string='Prescription', required=True, tracking=True)
    priority = fields.Selection([("0","Normal"),("1","Low"),("2","High"),("3","Very High")], string='Priority', required=True, default="0" , tracking=2)
    state = fields.Selection([("draft","Draft"),("create","Created"),("ongoing","Ongoing"),("done","Done"),("cancel","Canceled")], default="draft", string='Status', required=True, tracking=3)
    pharmacy_line_ids = fields.One2many('hms.appointment.pharmacy.line','appointment_id',string="Pharmacy line")
    hide_sale_price = fields.Boolean(string="Hide sale price", required=True, tracking=True)
    tag_ids = fields.Many2many('hms.tag','hms_appointment_has_tags','hms_appointment_id','tag_id',string="Tags", tracking=True)
    total_price = fields.Float(string='Total price', required=False, tracking=True, store=True, default="0",compute="_compute_cal_total_price")
    progress = fields.Integer(string='Progress', compute="_compute_progress",default="25")
    duration = fields.Float(string='Duration', tracking=True,default="1")
    company_id = fields.Many2one('res.company',string="Company", tracking=True, ondelete="cascade",default=lambda self : self.env.company )
    currency_id = fields.Many2one('res.currency',string="Currency", tracking=True, related='company_id.currency_id' )
    
    # @api.model_create_multi
    # def create(self, vals):
    #     for row in vals:
    #         row['reference'] = self.env['ir.sequence'].next_by_code('hms.appointment.reference')
    #     return super(HMSAppointment, self).create(vals)
    
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('hms.appointment.reference')
        res = super(HMSAppointment, self).create(vals)
        res.set_hms_appointment_pharmacy_line(self)
        return res
    
    def write(self, vals):
        if not self.reference and not vals.get('reference'):
            self.reference = self.env['ir.sequence'].next_by_code('hms.appointment.reference')
        res = super(HMSAppointment, self).write(vals)
        self.set_hms_appointment_pharmacy_line()
        return res
    
    def unlink(self):
        passValidation = True
        errorMessage = "Error"
        if self.state != 'draft':
            passValidation = False
            errorMessage = _("You can only delete appoinment with 'Draft' status.")  
        if passValidation == True :
            return super(HMSAppointment,self).unlink()
        else:
            raise ValidationError(_(errorMessage))   
        
    def action_send_mail(self): 
        template = self.env.ref('hospital_management_system.appoinment_mail_templete')
        for row in self:
            if row.patient_id.email:
                c_subject = 'Test mail for Patient %s' %row.patient_id.name
                email_values = {'subject': c_subject}
                template.send_mail(row.id, force_send=True,email_values=email_values)
            else:
                raise ValidationError(_("Pation has no email."))  
        
    @api.onchange('pharmacy_line_ids','pharmacy_line_ids.qty')
    def _onchange_cal_total_price(self):
        c_total_price = 0
        for perLine in self.pharmacy_line_ids:
            c_total_price =  c_total_price + perLine.price
        
        self.total_price =  c_total_price
    
    @api.depends('pharmacy_line_ids','pharmacy_line_ids.qty')
    def _compute_cal_total_price(self):
        c_total_price = 0
        for perLine in self.pharmacy_line_ids:
            c_total_price =  c_total_price + perLine.price
        
        self.total_price =  c_total_price
            
    @api.depends("name")
    def _compute_capitalize_name(self):
        if self.name:
            self.capitalize_name = self.name.upper()
        else:
            self.capitalize_name = self.name
            
    def name_get(self):
        res = []
        for row in self:
            name = f'{row.reference} - {row.name}'
            res.append((row.id,name))
        return res
    
    def cancel_appointment(self):
        passValidation = False
        errorMessage = "Error"
        cancel_appoinment_before_days = self.env['ir.config_parameter'].get_param("hospital_management_system.cancel_appoinment_before_days")
        for row in self:
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
            self.write({'state': 'cancel'})
            return {
                'effect' : {
                    'fadeout' : 'slow',
                    'message' : 'Successfully canceled.',
                    'type' : 'rainbow_man',
                }
            }
        else:
            raise ValidationError(_(errorMessage))
    
    # def cancel_appointment(self):
    #     action = self.env.ref("hospital_management_system.action_hms_cancel_appointment_view").read()[0]
    #     return action
        
    def create_appointment(self):
        
        errorCount = 0
        errorMessage = "Error"
        for row in self:
            if row.state != 'draft':
                errorCount = errorCount + 1 
                if row.state == 'create':
                    errorMessage = (_("Appoinment is created."))
                if row.state == 'done':
                    errorMessage = (_("Appoinment is  done."))
                elif row.state == 'cancel':
                    errorMessage = (_("Appoinment is canceled."))
                else:
                    errorMessage = (_("Only draft appoinment can be create."))
            
        if errorCount == 0 :
            self.write({'state': 'create'})
            return {
                'effect' : {
                    'fadeout' : 'slow',
                    'message' : 'Successfully create.',
                    'type' : 'rainbow_man',
                }
            }
        else:
            raise ValidationError(_(errorMessage))
        
    def ongoing_appointment(self):
        passValidation = False
        errorMessage = "Error"
        for row in self:
            if row.state == 'create':
                passValidation = True
            else:
                passValidation = False
                if row.state == 'ongoing':
                    errorMessage = (_("Appoinment is ongoing."))
                if row.state == 'done':
                    errorMessage = (_("Appoinment is  done."))
                elif row.state == 'cancel':
                    errorMessage = (_("Appoinment is canceled."))
                else:
                    errorMessage = (_("Only create appoinment can be ongoing."))
        if passValidation == True :
            self.write({'state': 'ongoing'})
            return {
                'effect' : {
                    'fadeout' : 'slow',
                    'message' : 'Successfully ongoing.',
                    'type' : 'rainbow_man',
                }
            }
        else:
            raise ValidationError(_(errorMessage))
        
    def done_appointment(self):
        passValidation = False
        errorMessage = "Error"
        for row in self:
            if row.state == 'ongoing':
                passValidation = True
            else:
                passValidation = False
                if row.state == 'done':
                    errorMessage = (_("Appoinment is already done."))
                elif row.state == 'cancel':
                    errorMessage = (_("Appoinment is already canceled."))
                else:
                    errorMessage = (_("Only ongoing appoinment can be done."))
        if passValidation == True :
            self.write({'state': 'done'})
            return {
                'effect' : {
                    'fadeout' : 'slow',
                    'message' : 'Successfully done.',
                    'type' : 'rainbow_man',
                }
            }
        else:
            raise ValidationError(_(errorMessage))
        
    @api.depends("state")
    def _compute_progress(self):
        progress = 0
        for row in self:
            if row.state == "draft":
                progress = random.randrange(0,25)
            elif row.state == "create":
                progress = 50
            elif row.state == "ongoing":
                progress = 75
            elif row.state == "done":
                progress = 100
            else:
                progress = 0
            row.progress = progress
            
    def redirect_action(self):
        return {
            'type' :  'ir.actions.act_url',
            'target' :  'new',
            'url'    : 'https://www.facebook.com/tahmid.farzan007/',
        }
        
    def create_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(_("Patient does not have phone"))
        message = "Hi *%s* , your appoinment number is *%s*. Thank you" % (self.patient_id.name,self.reference)
        whatsapp_api = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, message)
        
        self.message_post(body=message,subject="Whatapp message")
        
        # query = """ select id,name from hms_appointment where id = %s""" %self.id
        # self.env.cr.execute(query)
        # appointments = self.env.cr.fetchall() 
        # appointments = self.env.cr.dicfetchall()
        # print(appointments)
        return {
            'type' :  'ir.actions.act_url',
            'target' :  'new',
            'url'    : whatsapp_api,
        }
    def action_notification(self):
        
        action = self.env.ref("hospital_management_system.action_hms_patient_view")
        return {
            'type' :  'ir.actions.client',
            'tag' :  'display_notification',
            'params' : {
                'title' : "Open  patient record.",
                'message' : '%s',
                'type' : 'success',
                'links' : [
                    {
                        'label' : self.patient_id.name,
                        'url' : f'#action={action.id}&id={self.patient_id.id}&model=hms.patient',
                    }
                ],
                'sticky' : False,
            },
        }
        #message = 'Hello,Test.'
        # return {
        #     'type' :  'ir.actions.client',
        #     'tag' :  'display_notification',
        #     'params' : {
        #         'title' : "Open  patient record.",
        #         'message' : message,
        #         'type' : 'success',
        #         'sticky' : False,
        #     },
        # }
        
        
    def action_page_notification(self):
        
        action = self.env.ref("hospital_management_system.action_hms_patient_view")
        return {
            'type' :  'ir.actions.client',
            'tag' :  'display_notification',
            'params' : {
                'title' : "Open  patient record.",
                'message' : '%s',
                'type' : 'success',
                'links' : [
                    {
                        'label' : self.patient_id.name,
                        'url' : f'#action={action.id}&id={self.patient_id.id}&model=hms.patient',
                    }
                ],
                'sticky' : False,
                'next': {
                    'type' :  'ir.actions.act_window',
                    'res_model' : 'hms.patient',
                    'res_id' : self.patient_id.id,
                    'views' : [(False,'form')],
                }
            },
        }
        
    def set_hms_appointment_pharmacy_line(self):
        slNo = 0
        for line in self.pharmacy_line_ids:
            slNo += 1
            line.sl_no = slNo
        return
            
class HMSAppointmentPharmacyLine(models.Model):
    _name = 'hms.appointment.pharmacy.line'
    _description = 'Pharmacy line for hospital management system'
    
    _inherit = ['mail.thread','mail.activity.mixin']
    
    sl_no = fields.Integer(string='Sl no')
    product_id = fields.Many2one('product.product',string='Product', required=True, tracking=True)
    price_unit = fields.Float(string='Price (unit)', related='product_id.list_price',digits="Product Price")
    qty = fields.Integer(string='Qty', required=True, tracking=True, default="0")
    note = fields.Text(string='Note', required=False, tracking=True)
    appointment_id = fields.Many2one('hms.appointment',string='Appointment', tracking=True)
    currency_id = fields.Many2one('res.currency',string="Currency", tracking=True, related='appointment_id.currency_id' )
    price = fields.Float(string='Price',required=True, tracking=True, default="0",store="1",compute="_compute_calculate_price")
    monetary_price = fields.Monetary(string='Price (Monetary)', currency_field='currency_id' ,required=True, tracking=True, default="0",store="1",compute="_compute_calculate_price")
    
    @api.onchange('qty','price_unit')
    def _onchange_calculate_price(self):
        for row in self:
            row.price = (row.qty * row.price_unit)
            row.monetary_price = (row.qty * row.price_unit)
        
    @api.depends('qty','price_unit')
    def _compute_calculate_price(self):
        for row in self:
            row.price = (row.qty * row.price_unit)
            row.monetary_price = (row.qty * row.price_unit)