from odoo import api, fields, models




class XLSUploadWizard(models.TransientModel):
    _name = 'repart.outilidades.wizard'

    ano = fields.Selection([('2021','2021'),('2022','2022')],string="Año")
    
    
    
    def year_report_xlsx(self):
        self.env.context = dict(self.env.context)
        self.env.context.update({'ano': self.ano})
        return self.env.ref('nomina_cfdi_extras_ee.reparto_utilidades_data').report_action(self)
    
    
class PartnerXlsx(models.AbstractModel):
    _name = 'report.nomina_cfdi_extras_ee.reparto_utilidades_data'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        row = 1
        payslip_objs = self.env['hr.payslip'].search([])
        year = payslip_objs.filtered(lambda d: d.fecha_pago.year == int(self.env.context.get('ano')))
        if year:
            sheet = workbook.add_worksheet('xls report')
            format1 = workbook.add_format({'font_size': 10 , 'align':'vcenter', 'bold': True})
            sheet.write(0,0,'No. Empleado',format1)
            sheet.write(0,1,'Nombre',format1)
            sheet.write(0,2,'Dias laborados',format1)
            sheet.write(0,3,'Total percepcioens',format1) 
         
            for ps in year:
                format2 = workbook.add_format({'font_size': 9 , 'align':'vcenter',})
                sheet.write(row,0,ps.employee_id.name,format2)
                sheet.write(row,1,ps.employee_id.name,format2)
                sum_data = ps.worked_days_line_ids.filtered(lambda d: d.code == 'WORK100')              
                sheet.write(row,2,sum_data.number_of_days,format2)
                line_obj = ps.line_ids.filtered(lambda d: d.code == 'TPER')
                sheet.write(row,3,len(line_obj),format2)
                row = row+1
            row = row+1    
           
        
    
    
    
    
        