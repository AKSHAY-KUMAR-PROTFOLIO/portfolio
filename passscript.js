let pass = document.getElementById("inputbox");
let msg = document.getElementById("message");
let str = document.getElementById("strength");

pass.addEventListener('input', () => {
    if (pass.value.length > 0){
        msg.style.display = "block";
    }
    else{
        msg.style.display = "none";
    }
    if (pass.value.length < 4){
        str.innerHTML ="weak";
        msg.style.color = "red"
        pass.style.borderColor = "red"

    }else if (pass.value.length >= 4 && pass.value.length < 8 ){
        str.innerHTML ="medium";
        msg.style.color = "yellow"
        pass.style.borderColor = "yellow"

    }else if (pass.value.length >= 8 ){
        str.innerHTML ="strong";
        msg.style.color = "#26d730"
        pass.style.borderColor = "#26d730"
    }
})