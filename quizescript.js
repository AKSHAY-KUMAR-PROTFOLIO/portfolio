const questionContainer = document.getElementById('question-container');
const questionElement = document.getElementById('question');
const answerButtons = document.getElementById('answer-buttons');
const nextButton = document.getElementById('next-button');

let currentQuestionIndex = 0;
let score = 0;

const questions = [
    {
        question: "What is the capital of France?",
        answers: [
            { text: "Paris", correct: true },
            { text: "Berlin", correct: false },
            { text: "Madrid", correct: false },
            { text: "Rome", correct: false }
        ]
    },
    {
        question: "Which planet is known as the Red Planet?",
        answers: [
            { text: "Earth", correct: false },
            { text: "Mars", correct: true },
            { text: "Jupiter", correct: false },
            { text: "Venus", correct: false }
        ]
    },
    {
        question: "What is the largest mammal?",
        answers: [
            { text: "Elephant", correct: false },
            { text: "Blue Whale", correct: true },
            { text: "Giraffe", correct: false },
            { text: "Hippopotamus", correct: false }
        ]
    },
    {
        question: "What is the capital of Japan?",
        answers: [
            { text: "Beijing", correct: false },
            { text: "Seoul", correct: false },
            { text: "Tokyo", correct: true },
            { text: "Bangkok", correct: false }
        ]
    },
    {
        question: "Which gas do plants use for photosynthesis?",
        answers: [
            { text: "Carbon Monoxide", correct: false },
            { text: "Oxygen", correct: false },
            { text: "Carbon Dioxide", correct: true },
            { text: "Nitrogen", correct: false }
        ]
    }
];

function showQuestion(question) {
    questionElement.innerText = question.question;
    answerButtons.innerHTML = '';
    nextButton.disabled = true;

    question.answers.forEach(answer => {
        const button = document.createElement('button');
        button.innerText = answer.text;
        button.classList.add('btn');
        button.addEventListener('click', (e) => selectAnswer(e, answer.correct));
        answerButtons.appendChild(button);
    });
}

function selectAnswer(event, correct) {
    const selectedButton = event.target;
    const buttons = answerButtons.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.disabled = true;
        const isCorrect = questions[currentQuestionIndex].answers.find(a => a.text === button.innerText).correct;
        button.style.backgroundColor = isCorrect ? "#00cc66" : "#cc3333";
        button.style.color = "#fff";
    });

    if (correct) {
        score++;
    }

    nextButton.disabled = false;
}

nextButton.addEventListener('click', () => {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion(questions[currentQuestionIndex]);
    } else {
        showResults();
    }
});

function showResults() {
    questionContainer.innerHTML = `
        <h2>Quiz Complete</h2>
        <p>Your score: ${score} out of ${questions.length}</p>
    `;
    answerButtons.innerHTML = '';
    nextButton.style.display = 'none';
}

showQuestion(questions[currentQuestionIndex]);
