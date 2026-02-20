var cursor = document.querySelector('.custom-cursor');

window.addEventListener('mousemove',(e)=>{
    console.log(e.clientX, e.clientY);
    var x = e.clientX;
    var y = e.clientY;
    cursor.style.top=`${y+10}px`;
    cursor.style.left=`${x+10}px`;
});

$(document).ready(function () {
    $(function () {
        $('li a').click(function (e) {
            e.preventDefault();
            $('a').removeClass('active');
            $(this).addClass('active');
        });
    });
});


const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-links a');

function removeActive() {
  navLinks.forEach(link => link.classList.remove('active'));
}

function setActiveLink() {
  let currentSection = '';
  
  sections.forEach(section => {
    const sectionTop = section.offsetTop - 150; // adjust for navbar height
    if (window.scrollY >= sectionTop) {
      currentSection = section.getAttribute('id');
    }
  });

  removeActive();
  if(currentSection) {
    const activeLink = document.querySelector(`.nav-links a[href="#${currentSection}"]`);
    if(activeLink) activeLink.classList.add('active');
  }
}

// Highlight on scroll
window.addEventListener('scroll', setActiveLink);
window.addEventListener('load', setActiveLink);

// Smooth scroll on click
navLinks.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const targetId = link.getAttribute('href').substring(1);
    const targetSection = document.getElementById(targetId);
    if(targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

