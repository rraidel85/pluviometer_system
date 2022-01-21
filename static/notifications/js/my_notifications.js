
function show_error_notification(title, message) {
	Lobibox.notify('error', {
		title: title,
		position: 'top',
		msg: message
	});
}
function show_info_notification(title, message) {
	Lobibox.notify('info', {
		title: title,
		position: 'top',
		msg: message
	});
}

function show_warning_notification(title, message) {
	Lobibox.notify('warning', {
		title: title,
		position: 'top',
		msg: message
	});
}

function show_success_notification(title, message) {
	Lobibox.notify('success', {
		title: title,
		position: 'top',
		msg: message
	});
}
