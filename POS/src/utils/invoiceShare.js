import { call } from 'frappe-ui'

export async function sendInvoiceEmail({
  invoiceName,
  recipients = [],
  subject = '',
  message = '',
  printFormat = '',
  letterhead = 1,
}) {
  return await call('pos_next.api.invoice_share.send_invoice_email', {
    invoice_name: invoiceName,
    recipients,
    subject,
    message,
    print_format: printFormat,
    letterhead,
  })
}

export async function getInvoiceWhatsappShare({
  invoiceName,
  phone = '',
  message = '',
  printFormat = '',
  letterhead = 1,
}) {
  return await call('pos_next.api.invoice_share.get_invoice_whatsapp_share', {
    invoice_name: invoiceName,
    phone,
    message,
    print_format: printFormat,
    letterhead,
  })
}
