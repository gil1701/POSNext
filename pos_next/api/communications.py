import frappe
from frappe import _
import json

@frappe.whitelist()
def send_invoice_email(invoice_name, email, print_format=None):
    """
    Sends the invoice PDF via email.
    """
    if not invoice_name or not email:
        frappe.throw(_("Invoice Name and Email are required"))

    # Check if invoice exists
    if not frappe.db.exists("Sales Invoice", invoice_name):
        frappe.throw(_("Invoice {0} not found").format(invoice_name))

    try:
        # Get PDF content
        pdf_content = frappe.get_print("Sales Invoice", invoice_name, print_format, as_pdf=True)

        # Send email
        frappe.sendmail(
            recipients=[email],
            subject=_("Invoice {0}").format(invoice_name),
            message=_("Please find attached the invoice {0}").format(invoice_name),
            attachments=[{
                "fname": f"{invoice_name}.pdf",
                "fcontent": pdf_content
            }]
        )
        return {"status": "success", "message": _("Email sent successfully")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Send Invoice Email Error"))
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_whatsapp_link(invoice_name, mobile_no, print_format=None):
    """
    Generates a WhatsApp link with a message and optionally a link to the invoice.
    Note: Direct file attachment via WhatsApp link is not possible.
    We'll provide a text message with the invoice details and a link if possible.
    """
    if not invoice_name or not mobile_no:
        frappe.throw(_("Invoice Name and Mobile Number are required"))

    doc = frappe.get_doc("Sales Invoice", invoice_name)

    # Clean mobile number
    mobile_no = "".join(filter(str.isdigit, mobile_no))

    # Construct message
    message = _("Hello, here is your invoice {0} for an amount of {1}").format(
        invoice_name,
        frappe.format_value(doc.grand_total, doc.meta.get_field("grand_total"), doc)
    )

    # If we have a public URL or want to point to the portal
    # base_url = frappe.utils.get_url()
    # message += f"\nView online: {base_url}/printview?doctype=Sales Invoice&name={invoice_name}"

    encoded_message = frappe.utils.data.quote(message)
    whatsapp_url = f"https://wa.me/{mobile_no}?text={encoded_message}"

    return {"status": "success", "link": whatsapp_url}
