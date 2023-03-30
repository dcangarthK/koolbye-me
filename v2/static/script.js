$(document).ready(function () {
    // show alert when form submitted successfully
    if ($(".alert-success").length) {
        $(".alert-success").fadeTo(2000, 500).slideUp(500, function () {
            $(".alert-success").slideUp(500);
        });
    }
    const switchers = [...document.querySelectorAll('.switcher')]

    switchers.forEach(item => {
        item.addEventListener('click', function() {
            switchers.forEach(item => item.parentElement.classList.remove('is-active'))
            this.parentElement.classList.add('is-active')
	})
})
});
