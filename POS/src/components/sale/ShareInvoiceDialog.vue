<script setup>
import { ref, watch, computed } from "vue";
import { Dialog, Button, FeatherIcon, call } from "frappe-ui";
import { __ } from "@/utils/translation";
import { useToast } from "@/composables/useToast";

const props = defineProps({
	show: Boolean,
	invoiceName: String,
	initialEmail: String,
	initialMobile: String,
	type: {
		type: String,
		default: "email", // 'email' or 'whatsapp'
	},
});

const emit = defineEmits(["update:show", "close"]);
const { showSuccess, showError } = useToast();

const show = computed({
	get: () => props.show,
	set: (value) => emit("update:show", value),
});

const loading = ref(false);
const email = ref(props.initialEmail || "");
const mobile = ref(props.initialMobile || "");

watch(
	() => props.show,
	(newVal) => {
		if (newVal) {
			email.value = props.initialEmail || "";
			mobile.value = props.initialMobile || "";
		}
	}
);

async function handleAction() {
	if (props.type === "email") {
		await sendEmail();
	} else {
		await openWhatsApp();
	}
}

async function sendEmail() {
	if (!email.value) {
		showError(__("Please enter a valid email address"));
		return;
	}

	loading.value = true;
	try {
		const res = await call("pos_next.api.communications.send_invoice_email", {
			invoice_name: props.invoiceName,
			email: email.value,
		});

		if (res.status === "success") {
			showSuccess(__("Email sent successfully"));
			show.value = false;
		} else {
			throw new Error(res.message);
		}
	} catch (err) {
		showError(err.message);
	} finally {
		loading.value = false;
	}
}

async function openWhatsApp() {
	if (!mobile.value) {
		showError(__("Please enter a valid mobile number"));
		return;
	}

	loading.value = true;
	try {
		const res = await call("pos_next.api.communications.get_whatsapp_link", {
			invoice_name: props.invoiceName,
			mobile_no: mobile.value,
		});

		if (res.status === "success" && res.link) {
			window.open(res.link, "_blank");
			show.value = false;
		} else {
			throw new Error(res.message || __("Could not generate WhatsApp link"));
		}
	} catch (err) {
		showError(err.message);
	} finally {
		loading.value = false;
	}
}
</script>

<template>
	<Dialog
		v-model="show"
		:options="{
			title: type === 'email' ? __('Send by Email') : __('Send by WhatsApp'),
			size: 'sm',
		}"
	>
		<template #body-content>
			<div class="py-4">
				<div v-if="type === 'email'">
					<label class="block text-sm font-medium text-gray-700 mb-1">
						{{ __("Email Address") }}
					</label>
					<input
						v-model="email"
						type="email"
						class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
						:placeholder="__('customer@example.com')"
						@keyup.enter="handleAction"
					/>
				</div>
				<div v-else>
					<label class="block text-sm font-medium text-gray-700 mb-1">
						{{ __("Mobile Number") }}
					</label>
					<input
						v-model="mobile"
						type="text"
						class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
						:placeholder="__('e.g. +1234567890')"
						@keyup.enter="handleAction"
					/>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex gap-2">
				<Button variant="subtle" @click="show = false">
					{{ __("Cancel") }}
				</Button>
				<Button
					variant="solid"
					theme="blue"
					:loading="loading"
					@click="handleAction"
				>
					{{ type === 'email' ? __('Send Email') : __('Open WhatsApp') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>
