# POSNext: Email y WhatsApp para factura completada

Archivos incluidos:

- `pos_next/api/invoice_share.py`
- `POS/src/utils/invoiceShare.js`
- `POS/src/components/sale/InvoiceShareDialog.vue`

## Modificación necesaria en el componente donde está el botón Imprimir

En el componente donde POSNext muestra el botón de imprimir factura después de completar el pedido, normalmente `POS/src/components/sale/POSSale.vue` o el componente de receipt/result, agrega:

```js
import InvoiceShareDialog from '@/components/sale/InvoiceShareDialog.vue'
```

En `setup`/estado del componente:

```js
const showInvoiceEmailDialog = ref(false)
const showInvoiceWhatsappDialog = ref(false)
```

Junto al botón de imprimir, agrega estos dos botones:

```html
<button
  class="btn btn-sm btn-primary"
  :disabled="!completedInvoiceName"
  @click="showInvoiceEmailDialog = true"
>
  {{ __('Email') }}
</button>

<button
  class="btn btn-sm btn-success"
  :disabled="!completedInvoiceName"
  @click="showInvoiceWhatsappDialog = true"
>
  {{ __('WhatsApp') }}
</button>

<InvoiceShareDialog
  v-model="showInvoiceEmailDialog"
  mode="email"
  :invoice-name="completedInvoiceName"
  :default-email="customer?.email_id || customer?.email || ''"
/>

<InvoiceShareDialog
  v-model="showInvoiceWhatsappDialog"
  mode="whatsapp"
  :invoice-name="completedInvoiceName"
  :default-phone="customer?.mobile_no || customer?.mobile || customer?.phone || ''"
/>
```

Cambia `completedInvoiceName` por la variable real que contenga el nombre de la `Sales Invoice` creada, por ejemplo `submittedInvoice.name`, `lastInvoice.name`, `invoice.name` o similar.

## Build

```bash
bench --site TU-SITIO clear-cache
bench build --app pos_next
bench --site TU-SITIO migrate
bench restart
```
