let input = document.getElementById('inputbox');
let buttons = document.querySelectorAll('button');

let string = "";
let arr = Array.from(buttons);

arr.forEach(button => {
    button.addEventListener('click', (e) => {
        const btn = e.target.innerHTML;

        if (btn === '=') {
            try {
                string = eval(string.replace(/x/g, '*'));
                input.value = string;
            } catch (err) {
                input.value = "Error";
                string = "";
            }
        } else if (btn === 'AC') {
            string = "";
            input.value = string;
        } else if (btn === 'DE') {
            string = string.slice(0, -1);
            input.value = string;
        } else {
            string += btn;
            input.value = string;
        }
    });
});
