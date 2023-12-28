window.onload = function() {
    document.getElementById('history-tab').classList.add("active");
    document.getElementById('history-tab').classList.add("gradient-custom-2");
};
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}