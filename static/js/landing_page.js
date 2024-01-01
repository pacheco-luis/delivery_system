
// to add responsiveness to navigation menue
const menueBtn = document.querySelector(".menue-btn")
const navigation = document.querySelector(".navigation")

menueBtn.addEventListener("click", () => {
    menueBtn.classList.toggle("active");
    navigation.classList.toggle("active");
})

// for video slider navigation
const btns = document.querySelectorAll(".nav-btn")
const slides = document.querySelectorAll(".video-slide")
const contents = document.querySelectorAll(".content")

var sliderNav = function (manual) {
    btns.forEach((btn) => {
        btn.classList.remove("active");
    });

    slides.forEach((slide) => {
        slide.classList.remove("active");
    });

    contents.forEach((content) => {
        content.classList.remove("active");
    });

    btns[manual].classList.add("active");
    slides[manual].classList.add("active");
    contents[manual].classList.add("active");
}

btns.forEach((btn, i) => {
    btn.addEventListener("click", () => {
        sliderNav(i);
    });
});

// function myFunction() {
//     var popupcontainer = document.getElementById("popup-container-button");
//     popupcontainer.classList.toggle("show");
// }

function register() {
    var popupcontainer = document.getElementById("popup-container-button-reg");
    popupcontainer.classList.toggle("show");
}

function login() {
    var popupcontainer = document.getElementById("popup-container-button-log");
    popupcontainer.classList.toggle("show");
}

// document.getElementById("reg-driver").onclick = function () {
//     location.href = "/register/driver/";
// };

// document.getElementById("reg-driver").onclick = function () {
//     location.href = "/register/driver/";
// };

// document.getElementById("reg-customer").onclick = function () {
//     location.href = "/register/customer/";
// };

document.getElementById("reg-driver").onclick = function () {
    location.href = "/register/driver/";
};

document.getElementById("reg-customer").onclick = function () {
    location.href = "/register/customer/";
};

document.getElementById("log-driver").onclick = function () {
    location.href = "/login/driver/";
}

document.getElementById("log-customer").onclick = function () {
    location.href = "/login/customer/";
}

