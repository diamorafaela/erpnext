from erpnext.accounts.doctype.subscription.subscription import *


self = frappe.get_doc('Subscription', 'ACC-SUB-2019-00040')

invoice = frappe.new_doc('Sales Invoice')
invoice.set_posting_time = 1
invoice.posting_date = nowdate()
invoice.customer = self.customer
invoice.subscription = self.name

# Si solo tiene un plan aplicamos esa lista de precios a la factura
if len(self.plans) == 1:
    invoice.selling_price_list = frappe.get_value("Subscription Plan", self.plans[0].plan, 'price_list')

# Subscription is better suited for service items. I won't update `update_stock`
# for that reason
items_list = self.get_items_from_plans(self.plans, prorate)
for item in items_list:
    invoice.append('items', item)

# Taxes
if self.tax_template:
    invoice.taxes_and_charges = self.tax_template
    invoice.set_taxes()

# Due date
invoice.append(
    'payment_schedule',
    {
        'due_date': add_days(invoice.posting_date, cint(self.days_until_due)),
        'invoice_portion': 100
    }
)

# Discounts
if self.additional_discount_percentage:
    invoice.additional_discount_percentage = self.additional_discount_percentage

if self.additional_discount_amount:
    invoice.discount_amount = self.additional_discount_amount

if self.additional_discount_percentage or self.additional_discount_amount:
    discount_on = self.apply_additional_discount
    invoice.apply_additional_discount = discount_on if discount_on else 'Grand Total'

# Subscription period
invoice.from_date = self.current_invoice_start
invoice.to_date = self.current_invoice_end

invoice.set_missing_values()
# invoice.flags.ignore_mandatory = True
# invoice.save()
# invoice.submit()

doc = invoice
