document.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('.compare__label').forEach((item) => {
		const input = item.querySelector('input');
		const button = item.querySelector('.btn');

		input.addEventListener('change', (e) => {
			if (e.target.files.length) {
				button.textContent = e.target.files[0].name;
			} else {
				button.textContent = 'Выбрать файл';
			}
		});
	});

	const createFileLabel = document.querySelector('.create__file-label');
	const createFileInput = createFileLabel.querySelector('input');
	const createFileButton = createFileLabel.querySelector('.btn');

	createFileInput.addEventListener('change', (e) => {
		if (e.target.files.length) {
			createFileButton.textContent = e.target.files[0].name;
		} else {
			createFileButton.textContent = 'Выбрать файл';
		}
	});
});
