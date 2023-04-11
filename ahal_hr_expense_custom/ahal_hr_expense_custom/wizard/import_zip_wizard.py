# -*- coding: utf-8 -*-
import zipfile
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
from datetime import datetime
from base64 import b64decode
from base64 import b64encode
from zipfile import ZipFile
import os
import json
import xml.etree.cElementTree as ET
import base64

class ImportZipWizard(models.TransientModel):
    _name = "import.zip.wizard"
    _description = "Import ZIP"
       
    file_name = fields.Char(string="Archivo ZIP" )
    file_file = fields.Binary(string='Archivo ZIP')
    msg = fields.Html(string='Mensaje', default=False)    
    line_ids = fields.One2many(string="XMLs", comodel_name='import.zip.wizard.line', inverse_name='wizard_id', )

    @api.onchange('file_file')
    def _onchange_file_file(self):
        if self.file_file:
            if 1:#try:
                # Se lee el archivo zip
                zip_file = open('./'+self.file_name,"wb")
                zip_file.write(b64decode(self.file_file))
                zip_file.close()
                #
                self.msg = False
                if not zipfile.is_zipfile(self.file_name):
                    self.msg = "<span style='color:red;'>No es un archivo zip válido.</span>"
                    self.file_file = False
                    self.line_ids = False
                    #                      
                    return {        
                        'name': _("Resultado"),                         
                        'view_type': 'form',        
                        'view_mode': 'form',        
                        'res_model': 'import.zip.wizard', 
                        'res_id': self.id,                  
                        'type': 'ir.actions.act_window',        
                        'target': 'new',    
                    }
                #
                with ZipFile('./'+self.file_name, 'r') as zf:
                    #                
                    for file in zf.namelist():                    
                        if not file.endswith('.xml') or 'MACOSX' in file:
                            continue                                                  
                        with zf.open(file) as f:                       
                            vals = {
                                'file_file': b64encode(f.read()),
                                'file_name': file,
                                'wizard_id': self.id
                            }
                            self.env['import.zip.wizard.line'].create(vals)  
                    #
                    return {        
                        'name': _("Resultado"),                         
                        'view_type': 'form',        
                        'view_mode': 'form',        
                        'res_model': 'import.zip.wizard', 
                        'res_id': self.id,                  
                        'type': 'ir.actions.act_window',        
                        'target': 'new',    
                    }
            # except:
            #     self.msg = "<span style='color:red;'>Error desconocido</span>"
            #     #                      
            #     return {        
            #         'name': _("Resultado"),                         
            #         'view_type': 'form',        
            #         'view_mode': 'form',        
            #         'res_model': 'import.zip..wizard', 
            #         'res_id': self.id,                  
            #         'type': 'ir.actions.act_window',        
            #         'target': 'new',    
            #     }
        else:
            self.line_ids = False
            self.msg = False
            return {        
                    'name': _("Resultado"),                         
                    'view_type': 'form',        
                    'view_mode': 'form',        
                    'res_model': 'import.zip..wizard', 
                    'res_id': self.id,                  
                    'type': 'ir.actions.act_window',        
                    'target': 'new',    
                }

    def _parse_xml_cfdi(self,xml=False):
        # 
        if not xml:
            return False
        #
        root = ET.fromstring(xml)
        #                        
        root_tag = root.tag.replace('Comprobante','')
        # Emisor
        emisor = ''
        # RegimenFiscal
        RegimenFiscal = ''
        for e in root.findall(root_tag + 'Emisor'):    
            emisor = e.get('Rfc')
            rs_emisor = e.get('Nombre') 
            RegimenFiscal = e.get('RegimenFiscal')                       
        # Receptor
        receptor = ''
        UsoCFDI = ''
        for e in root.findall(root_tag + 'Receptor'):    
            receptor = e.get('Rfc')
            rs_receptor = e.get('Nombre')   
            UsoCFDI = e.get('UsoCFDI')             
        # uuid
        uuid = ''
        for c in root.findall(root_tag + 'Complemento'):
            for e in c:        
                uuid = e.get('UUID')
        # fechaTimbrado
        fechaTimbrado = ''
        for c in root.findall(root_tag + 'Complemento'):
            for e in c:        
                fechaTimbrado = e.get('FechaTimbrado')    
        # RfcProvCertif
        for c in root.findall(root_tag + 'Complemento'):
            for e in c:        
                RfcProvCertif = e.get('RfcProvCertif')    
        
        # TotalImpuestosTrasladados                            
        TotalImpuestosTrasladados = 0
        for e in root.findall(root_tag + 'Impuestos'):    
            TotalImpuestosTrasladados = e.get('TotalImpuestosTrasladados')
        # TotalImpuestosRetenidos                            
        TotalImpuestosRetenidos = 0
        for e in root.findall(root_tag + 'Impuestos'):    
            TotalImpuestosRetenidos = e.get('TotalImpuestosRetenidos')
        # Conceptos
        Conceptos = '['
        for e in root.findall(root_tag + 'Conceptos'):            
            for c in e.findall(root_tag + 'Concepto'):
                # Impuestos trasladados
                Traslados = '['
                for i in c.findall(root_tag + 'Impuestos'):        
                    for ts in i.findall(root_tag + 'Traslados'):
                        for t in ts.findall(root_tag + 'Traslado'):
                            traslado = """
                                'Base': '{}',
                                'Importe': '{}',
                                'Impuesto': '{}',
                                'TasaOCuota': '{}',
                                'TipoFactor': '{}'                    
                                """.format(t.get('Base'),t.get('Importe'),t.get('Impuesto'),t.get('TasaOCuota'),t.get('TipoFactor'))
                            Traslados += '{' + traslado + '},'
                Traslados = Traslados[:-1] + ']' if len(Traslados) > 1 else '[]'

                concepto = """
                    'Cantidad': '{}', 
                    'ClaveProdServ': '{}', 
                    'ClaveUnidad': '{}', 
                    'Descripcion': '{}', 
                    'Descuento': '{}', 
                    'Importe': '{}', 
                    'ValorUnitario': '{}',
                    'Traslados': {}""".format(c.get('Cantidad'),c.get('ClaveProdServ'),c.get('ClaveUnidad'),c.get('Descripcion'),c.get('Descuento'),c.get('Importe'),c.get('ValorUnitario'),Traslados)
                Conceptos += '{' + concepto + '},'
        Conceptos = Conceptos[:-1] + ']'                                  
        # TipoDeComprobante
        tiposComprobante = {'I':'Ingreso','E':'Egreso','T':'Traslado','P':'Pago','N': 'Nómina'}       

        vals = {
            'emisor': emisor,
            'rs_emisor': rs_emisor,
            'receptor': receptor,
            'rs_receptor': rs_receptor,
            'TipoDeComprobante': tiposComprobante.get(root.get('TipoDeComprobante')),
            'Serie': root.get('Serie'),
            'Folio': root.get('Folio'),
            'Fecha': root.get('Fecha') ,
            'SubTotal': root.get('SubTotal'),
            'Descuento': root.get('Descuento'),
            'TotalImpuestosTrasladados': TotalImpuestosTrasladados,
            'TipoImpuestoTrasladado': '',
            'TotalImpuestosRetenidos': TotalImpuestosRetenidos,
            'TipoImpuestoRetenido': '',
            'Total': root.get('Total'),
            'MetodoPago': root.get('MetodoPago'),
            'FormaPago': root.get('FormaPago'),
            'Moneda': root.get('Moneda'),
            'TipoCambio': root.get('TipoCambio') or 1,
            'Version': root.get('Version'),
            'UsoCFDI': UsoCFDI,
            'RegimenFiscal': RegimenFiscal,
            'Conceptos': Conceptos,
            'uuid': uuid,
            'Fecha': root.get('Fecha'),
            'FechaTimbrado': fechaTimbrado,
            'RfcProvCertif': RfcProvCertif,
            'Conceptos': Conceptos
        }
        return vals

    def create_invoice(self, partner=False, invoice_date=False, conceptos=[]):
        #
        for rec in self:             
            # Se busca el partner y se crea si no existe
            partner_id = self.env['res.partner'].search([('name','=',partner)])     
            if not partner_id:
                partner_id = self.env['res.partner'].create({'name': partner})
            # Se crea la factura
            vals = {
                'partner_id' : partner_id.id,
                'move_type' : 'in_invoice',
                'state' : 'draft',
                'invoice_date': invoice_date
            }
            invoice_id = self.env['account.move'].create(vals)
            # Se obtienen los conceptos y se crea una linea para cada concepto
            cons = eval(conceptos)   
            for c in cons:              
                # Para cada traslado se busca un impuesto 
                traslados = c.get('Traslados')
                # Se buscan los impuestos 
                tax_ids = []
                total_concepto = 0
                for traslado in traslados:
                    total_concepto += float(traslado.get('Base')) + float(traslado.get('Importe'))
                    tax_id = self.env['account.tax'].search(
                    [
                        ('active','=',True),
                        ('type_tax_use','=','purchase'),
                        ('amount','=',100 * float(traslado.get('TasaOCuota')))
                    ])
                    if not tax_id:
                        raise UserError("No se ha configurado el impuesto tipo {} con tasa {}".format(traslado.get('Impuesto'),traslado('TasaOCuota')))
                    tax_ids.append((4,tax_id.id,0))
                    tax_repartition_line_id = self.env['account.tax.repartition.line'].search(
                        [('invoice_tax_id','=',tax_id.id),('company_id','=',self.env.company.id),('repartition_type','=','tax')], limit=1)
                    # Linea de impuesto
                    tax_line = {
                        'move_id' : invoice_id.id,
                        'account_id': tax_id.cash_basis_transition_account_id.id, 
                        'quantity' : 1,
                        'name': tax_id.name,
                        'price_unit': float(traslado.get('Importe')),           
                        'debit' : float(traslado.get('Importe')),
                        'tax_line_id': tax_id.id,
                        'tax_group_id': tax_id.tax_group_id.id,
                        'tax_base_amount': float(traslado.get('Base')),
                        'tax_repartition_line_id': tax_repartition_line_id.id if tax_repartition_line_id else False,
                        'exclude_from_invoice_tab' : True,
                        }                        
                    self.env['account.move.line'].with_context(check_move_validity=False).create(tax_line)                
                # Linea de débito
                descuento = 0
                try:
                    descuento = float(c.get('Descuento'))
                except:
                    descuento = 0
                debit_line = {
                    'move_id' : invoice_id.id,
                    'account_id' : invoice_id.journal_id.default_account_id.id,
                    'quantity' : float(c.get('Cantidad')),
                    'price_unit' : float(c.get('ValorUnitario')) - descuento,
                    'debit' : (float(c.get('ValorUnitario')) - descuento) * float(c.get('Cantidad')),              
                    'product_id' : False,               
                    'name' : c.get('Descripcion'),
                    'tax_ids' : tax_ids if tax_ids else False
                }            
                self.env['account.move.line'].with_context(check_move_validity=False).create(debit_line)

                # Linea de crédito
                credit_line = {
                    'move_id' : invoice_id.id,
                    'account_id' : invoice_id.partner_id.property_account_payable_id.id,
                    'quantity' : float(c.get('Cantidad')),            
                    'credit' : total_concepto,
                    'exclude_from_invoice_tab' : True,
                    'tax_ids' : tax_ids if tax_ids else False
                    }
                self.env['account.move.line'].with_context(check_move_validity=False).create(credit_line)                                                                                
        return invoice_id
    
    def action_create_invoices(self):       
        #
        report_id = self.env['hr.expense.sheet'].browse(self.env.context.get('active_id'))
        for line in self.line_ids:            
            # Se lee el archivo xml
            xml_file = open('./'+line.file_name,"wb")
            xml_file.write(b64decode(line.file_file))
            xml_file.close()
            #
            vals = ""
            with open('./'+line.file_name) as f:    
                vals = self._parse_xml_cfdi(f.read())
                # Se busca el uuid
                invoice_id = self.env['account.move'].search([('uuid_xml','=',vals.get('uuid'))])
                if invoice_id:
                    raise UserError("""
                    El XML: {} 
                    UUID: {} 
                    Emisor: {} 
                    Importe ${} 
                    Ya existe en el sistema.""".format(line.file_name,vals.get('uuid'),vals.get('rs_emisor'),vals.get('Total')))
                if vals:                                                  
                    invoice_id = self.create_invoice(vals.get('rs_emisor'), vals.get('Fecha').split('T')[0], vals.get('Conceptos'))  
                    invoice_id.sheet_id = report_id.id                
                    invoice_id.uuid_xml = vals.get('uuid')   
                    # Attachment
                    self.env['ir.attachment'].create(
                    {
                        'name': line.file_name,
                        'type': 'binary',
                        'datas': f.read(),
                        'res_model': 'account.move',
                        'res_id': invoice_id.id,
                        'mimetype': 'application/xml'
                    })             
        return
                                                                                
    

class ImportZipWizardLine(models.TransientModel):
    _name = "import.zip.wizard.line"
    _description = "Import ZIP line"
       
    file_name = fields.Char(string="Archivo XML" )
    file_file = fields.Binary(string='Archivo XML')
    wizard_id = fields.Many2one(comodel_name='import.zip.wizard')