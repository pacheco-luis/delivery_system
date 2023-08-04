// ALERT
let alertClose = document.querySelectorAll('.alert__close');

alertClose.forEach((el) => {
    el.addEventListener('click', () => {
        let alertWrapper = el.closest(".alert");
        alertWrapper.style.display = 'none';
    })
})
