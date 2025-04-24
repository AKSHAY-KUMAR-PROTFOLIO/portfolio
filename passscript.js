let pass = document.getElementById("inputbox");
let msg = document.getElementById("message");
let str = document.getElementById("strength");
let generateBtn = document.getElementById("generateBtn");
let viewPasswordBtn = document.getElementById("viewPasswordBtn");

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
});

// Function to generate a strong password
function generateStrongPassword() {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_-+=<>?";
    let password = "";
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    pass.value = password;
    checkPasswordStrength(password); // Update password strength immediately
}

// Event listener for generate button
generateBtn.addEventListener('click', generateStrongPassword);

// Function to check the strength of the generated password
function checkPasswordStrength(password) {
    if (password.length < 4){
        str.innerHTML ="weak";
        msg.style.color = "red"
        pass.style.borderColor = "red"
    }else if (password.length >= 4 && password.length < 8 ){
        str.innerHTML ="medium";
        msg.style.color = "yellow"
        pass.style.borderColor = "yellow"
    }else if (password.length >= 8 ){
        str.innerHTML ="strong";
        msg.style.color = "#26d730"
        pass.style.borderColor = "#26d730"
    }
}

// Function to toggle password visibility
viewPasswordBtn.addEventListener('click', () => {
    if (pass.type === "password") {
        pass.type = "text";
        viewPasswordBtn.innerHTML = "Hide"; // Change button text
    } else {
        pass.type = "password";
        viewPasswordBtn.innerHTML = "View"; // Change button text
    }
});
