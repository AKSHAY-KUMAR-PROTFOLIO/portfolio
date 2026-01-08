
const clip = document.querySelectorAll('.clip');
for(let i = 0; i<clip.length; i++){
    clip[i].addEventListener('mouseenter', function(e){
        clip[i].play()
    })
    clip[i].addEventListener('mouseout', function(e){
        clip[i].pause()
    })
}

// Calling showTime function at every second
setInterval(showTime, 1000);
 
// Defining showTime funcion
function showTime() {
    // Getting current time and date
    let time = new Date();
    let hour = time.getHours();
    let min = time.getMinutes();
    let sec = time.getSeconds();
    am_pm = "AM";
 
    // Setting time for 12 Hrs format
    if (hour >= 12) {
        if (hour > 12) hour -= 12;
        am_pm = "PM";
    } else if (hour == 0) {
        hr = 12;
        am_pm = "AM";
    }
 
    hour =
        hour < 10 ? "0" + hour : hour;
    min = min < 10 ? "0" + min : min;
    sec = sec < 10 ? "0" + sec : sec;
 
    let currentTime =
         "Ending in "+
        hour +
        "Hours : " +
        min +
        "Mins : " +
        sec +
        "Sec";
 
    // Displaying the time
    document.getElementById(
        "clock"
    ).innerHTML = currentTime;
}
 
showTime();

