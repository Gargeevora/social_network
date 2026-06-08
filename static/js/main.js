// main.js - Social Network

document.addEventListener("DOMContentLoaded", function () {
  // Auto hide messages after 4 seconds
  const messages = document.querySelectorAll(".message");
  messages.forEach(function (msg) {
    setTimeout(function () {
      msg.remove();
    }, 4000);
  });

  // Profile dropdown toggle
  const profileBtn = document.querySelector(".nav-profile-btn");
  const profileDropdown = document.getElementById("profileDropdown");

  if (profileBtn && profileDropdown) {
    profileBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      profileDropdown.classList.toggle("active");
    });

    document.addEventListener("click", function (e) {
      if (!e.target.closest(".nav-profile-dropdown")) {
        profileDropdown.classList.remove("active");
      }
    });
  }
});


// Hamburger menu
const hamburgerBtn = document.getElementById('hamburgerBtn');
const mobileMenu = document.getElementById('mobileMenu');

if (hamburgerBtn && mobileMenu) {
    hamburgerBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        mobileMenu.classList.toggle('open');
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.mobile-menu') && !e.target.closest('.hamburger-btn')) {
            mobileMenu.classList.remove('open');
        }
    });
}