<template>
  <Dialog
    v-model="show"
    :options="{
      title: mode === 'email' ? __('Send Invoice by Email') : __('Share Invoice by WhatsApp'),
      size: 'sm',
    }"
  >
    <template #body-content>
      <div class="space-y-4 p-1">
        <div v-if="mode === 'email'" class="space-y-1">
          <label class="text-sm font-medium text-gray-700">{{ __('Email') }}</label>
          <input
            v-model.trim="email"
            type="email"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            :placeholder="__('customer@example.com')"
            @keyup.enter="submit"
          />
        </div>

        <div v-else class="space-y-1">
          <label class="text-sm font-medium text-gray-700">{{ __('WhatsApp Number') }}</label>
          <input
            v-model.trim="phone"
            type="tel"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-200"
            :placeholder="__('Example: 18095551234')"
            @keyup.enter="submit"
          />
          <p class="text-xs text-gray-500">
            {{ __('Use country code without +, spaces or dashes.') }}
          </p>
        </div>

        <div v-if="error" class="rounded-lg bg-red-50 p-2 text-sm text-red-700">
          {{ error }}
        </div>
      </div>
    </template>

    <template #actions>
      <Button variant="subtle" :disabled="loading" @click="show = false">
        {{ __('Cancel') }}
      </Button>
      <Button
        :variant="mode === 'email' ? 'solid' : 'solid'"
        :loading="loading"
        @click="submit"
      >
        {{ mode === 'email' ? __('Send Email') : __('Open WhatsApp') }}
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Button, Dialog } from 'frappe-ui'
import { sendInvoiceEmail, getInvoiceWhatsappShare } from '@/utils/invoiceShare'

const props = defineProps({
  modelValue: Boolean,
  mode: {
    type: String,
    default: 'email',
    validator: value => ['email', 'whatsapp'].includes(value),
  },
  invoiceName: {
    type: String,
    required: true,
  },
  defaultEmail: {
    type: String,
    default: '',
  },
  defaultPhone: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const show = ref(props.modelValue)
const email = ref(props.defaultEmail || '')
const phone = ref(props.defaultPhone || '')
const loading = ref(false)
const error = ref('')

watch(
  () => props.modelValue,
  value => {
    show.value = value
    if (value) {
      email.value = props.defaultEmail || ''
      phone.value = props.defaultPhone || ''
      error.value = ''
    }
  }
)

watch(show, value => emit('update:modelValue', value))

function notify(message, indicator = 'green') {
  if (window.frappe?.show_alert) {
    window.frappe.show_alert({ message, indicator })
  }
}

function cleanPhone(value) {
  return String(value || '').replace(/\D/g, '')
}

function validate() {
  error.value = ''

  if (!props.invoiceName) {
    error.value = __('Invoice not found.')
    return false
  }

  if (props.mode === 'email') {
    if (!email.value) {
      error.value = __('Please enter an email address.')
      return false
    }
    return true
  }

  phone.value = cleanPhone(phone.value)
  if (!phone.value) {
    error.value = __('Please enter a WhatsApp number.')
    return false
  }
  return true
}

async function submit() {
  if (!validate()) return

  loading.value = true
  try {
    if (props.mode === 'email') {
      await sendInvoiceEmail({
        invoiceName: props.invoiceName,
        recipients: [email.value],
      })
      notify(__('Invoice email queued successfully.'), 'green')
      show.value = false
      return
    }

    const response = await getInvoiceWhatsappShare({
      invoiceName: props.invoiceName,
      phone: phone.value,
    })

    const url = response?.whatsapp_url || response?.message?.whatsapp_url
    if (!url) {
      throw new Error(__('WhatsApp URL was not returned by the server.'))
    }

    window.open(url, '_blank', 'noopener,noreferrer')
    show.value = false
  } catch (err) {
    error.value = err?.messages?.[0] || err?.message || __('Unable to complete this action.')
    notify(error.value, 'red')
  } finally {
    loading.value = false
  }
}
</script>
