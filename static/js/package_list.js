window.onload = function() {
    document.getElementById('sidebar_active_requests_btn').classList.add("active_tab");
};
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}