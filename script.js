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




