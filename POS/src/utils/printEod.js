import { silentPrintDoc } from "./printInvoice";

const EOD_PRINT_FORMAT = "POS Next EOD Report";

export async function printEODReport(closingShiftName) {
	await silentPrintDoc("POS Closing Shift", closingShiftName, EOD_PRINT_FORMAT);
}

export function printEODReportInBrowser(closingShiftName) {
	const params = new URLSearchParams({
		doctype: "POS Closing Shift",
		name: closingShiftName,
		format: "POS Next EOD Report",
		no_letterhead: "1",
		trigger_print: "1",
		_t: Date.now().toString(),
	});

	const printWindow = window.open(
		`/printview?${params}`,
		"_blank",
		"width=800,height=600"
	);

	if (!printWindow) {
		throw new Error("Popup blocked — check browser settings.");
	}

	return true;
}
