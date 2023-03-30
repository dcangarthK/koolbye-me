
// `script.js`

// javascript
// Add behavior to picture descriptions
let descriptions = document.querySelectorAll('.description');

descriptions.forEach(description => {
	description.addEventListener('click', () => {
		description.classList.toggle('expanded');
	});
});
