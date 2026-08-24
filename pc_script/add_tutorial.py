# -*- coding: utf-8 -*-
import codecs

js = codecs.open('static/app.js', 'r', 'utf-8').read()

tutorial_js = '''
// TUTORIAL LOGIC
const tutorialSteps = [
    {
        title: "¡Bienvenido a BindDeck!",
        text: "Vamos a darte un rápido paseo para que descubras todo lo que puedes hacer con tu dispositivo."
    },
    {
        title: "Ajustes del Dispositivo",
        text: "En el panel de la izquierda puedes conectar tu ESP32, ya sea por USB o Wi-Fi, y cambiar el comportamiento de los LEDs y la pantalla OLED."
    },
    {
        title: "Configuración de Teclas",
        text: "En el panel de la derecha (Acción) puedes asignar atajos de teclado, abrir programas y cambiar las animaciones de cada tecla por separado."
    },
    {
        title: "Modo Prueba",
        text: "Arriba tienes el Modo Prueba. Si lo activas, puedes hacer clic en los botones de la pantalla virtual y arrastrar la rueda para simular su comportamiento en tiempo real."
    }
];

let currentTutorialStep = 0;

function showTutorialStep(step) {
    document.getElementById('tutorial-modal').style.display = 'flex';
    document.getElementById('tut-title').innerText = tutorialSteps[step].title;
    document.getElementById('tut-text').innerText = tutorialSteps[step].text;
    document.getElementById('tut-progress').innerText = (step + 1) + " / " + tutorialSteps.length;
    
    if (step === tutorialSteps.length - 1) {
        document.getElementById('tut-btn-next').innerText = "Finalizar";
    } else {
        document.getElementById('tut-btn-next').innerText = "Siguiente";
    }
}

function nextTutorialStep() {
    currentTutorialStep++;
    if (currentTutorialStep >= tutorialSteps.length) {
        closeTutorial();
    } else {
        showTutorialStep(currentTutorialStep);
    }
}

function closeTutorial() {
    document.getElementById('tutorial-modal').style.display = 'none';
    localStorage.setItem('tutorialSeen', 'true');
}

document.getElementById('tut-btn-next').addEventListener('click', nextTutorialStep);
document.getElementById('tut-btn-skip').addEventListener('click', closeTutorial);

document.getElementById('btn-tutorial').addEventListener('click', () => {
    currentTutorialStep = 0;
    showTutorialStep(0);
});

// Auto-show tutorial on first run
window.addEventListener('DOMContentLoaded', () => {
    if (!localStorage.getItem('tutorialSeen')) {
        currentTutorialStep = 0;
        showTutorialStep(0);
    }
});
'''

codecs.open('static/app.js', 'w', 'utf-8').write(js + '\n' + tutorial_js)
