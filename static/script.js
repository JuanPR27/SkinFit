/**
 * script.js
 * Lógica de Navegación del Formulario Multi-paso y Ajuste de Dimensiones
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Elementos del DOM
    const formSteps = document.querySelectorAll('.form-step');
    const form = document.getElementById('skinfit-form');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtn = document.getElementById('submit-btn');
    const indicator = document.getElementById('step-indicator');
    
    // 2. Variables de Estado
    let currentStep = 0;
    const totalSteps = formSteps.length;
    let isAnimating = false;

    // --- FUNCIONES CRUCIALES DE DIMENSIONES Y VALIDACIÓN ---

    /**
     * Ajusta dinámicamente la altura del contenedor del formulario (#skinfit-form)
     * al tamaño del paso activo. Esto soluciona el problema de que el contenido se corte.
     * @param {number} stepIndex - Índice del paso a medir.
     */
    function adjustFormHeight(stepIndex) {
        const stepElement = formSteps[stepIndex];
        const fieldset = stepElement.querySelector('fieldset');
        if (fieldset) {
            // Se usa la altura del fieldset + 100px para el espacio de los botones y padding.
            const height = fieldset.offsetHeight + 100; 
            form.style.minHeight = `${height}px`;
        }
    }

    /**
     * Valida los campos requeridos en el paso actual.
     * @param {number} stepIndex - Índice del paso a validar.
     * @returns {boolean} - true si es válido, false si no lo es.
     */
    function validateStep(stepIndex) {
        const step = formSteps[stepIndex];
        let isValid = true;
        
        // Valida inputs y selects usando la API de validación HTML5
        const requiredInputs = step.querySelectorAll('input[required], select[required]'); 
        requiredInputs.forEach(input => {
            if (!input.checkValidity()) {
                isValid = false;
                // Muestra el mensaje de error nativo del navegador
                input.reportValidity(); 
            }
        });
        
        // Nota: La validación de checkboxes (Paso 2) se omite, asumiendo que no es obligatorio marcar uno.
        
        return isValid;
    }

    // --- FUNCIÓN PRINCIPAL DE NAVEGACIÓN ---

    /**
     * Muestra un paso del formulario con animación de deslizamiento.
     * @param {number} newStepIndex - Índice del paso al que se desea ir.
     * @param {number} direction - 1 para avanzar (derecha), -1 para retroceder (izquierda).
     */
    function showStep(newStepIndex, direction = 1) { 
        if (isAnimating || newStepIndex < 0 || newStepIndex >= totalSteps) return;

        const prevStep = formSteps[currentStep];
        const nextStep = formSteps[newStepIndex];
        
        isAnimating = true;
        
        // 1. Iniciar la animación de SALIDA en el paso anterior
        // Se aplica la clase de animación de salida (ej: slide-out-left)
        prevStep.classList.remove('animate-slide-in-right');
        prevStep.classList.add(direction === 1 ? 'animate-slide-out-left' : 'animate-slide-in-right');
        
        // 2. Preparar el nuevo paso: Quitar 'active' al anterior y añadir al siguiente
        prevStep.classList.remove('active');
        nextStep.classList.add('active'); 

        // 3. Iniciar la animación de ENTRADA en el nuevo paso
        // Se aplica la clase de animación de entrada (ej: slide-in-right)
        nextStep.classList.remove('hidden', 'animate-slide-out-left', 'animate-slide-in-right');
        nextStep.classList.add(direction === 1 ? 'animate-slide-in-right' : 'animate-slide-out-left');

        // 4. Esperar a que la animación de SALIDA termine
        prevStep.addEventListener('animationend', function handler() {
            // Ocultar permanentemente el paso anterior y limpiar clases de animación
            prevStep.classList.remove('animate-slide-out-left', 'animate-slide-in-right');
            prevStep.classList.add('hidden');
            prevStep.removeEventListener('animationend', handler);

            // 5. Esperar a que la animación de ENTRADA termine
            nextStep.addEventListener('animationend', function handler() {
                // Limpiar clases de animación y ajustar la altura
                nextStep.classList.remove('animate-slide-in-right', 'animate-slide-out-left');
                adjustFormHeight(newStepIndex); 
                isAnimating = false;
                nextStep.removeEventListener('animationend', handler);
            }, { once: true });
        }, { once: true });
        
        currentStep = newStepIndex; // Actualizar el estado
        
        // 6. Actualizar visibilidad de los botones y el indicador
        prevBtn.classList.toggle('hidden', currentStep === 0); 
        nextBtn.classList.toggle('hidden', currentStep === totalSteps - 1); 
        submitBtn.classList.toggle('hidden', currentStep !== totalSteps - 1); 

        // Actualizar indicador visual
        indicator.querySelectorAll('div').forEach((dot, index) => {
            dot.classList.remove('bg-pink-500', 'w-12');
            dot.classList.add('bg-gray-300', 'w-8');
            if (index <= currentStep) {
                dot.classList.add('bg-pink-500', 'w-12'); 
                dot.classList.remove('bg-gray-300', 'w-8');
            }
        });
        
        // Asegurar que la vista se mantenga arriba
        window.scrollTo(0, 0); 
    }
    
    // --- MANEJADORES DE EVENTOS ---

    // Evento para avanzar
    nextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (validateStep(currentStep)) {
            showStep(currentStep + 1, 1); 
        }
    });

    // Evento para retroceder
    prevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentStep > 0) {
            showStep(currentStep - 1, -1); 
        }
    });

    // --- INICIALIZACIÓN ---
    
    // 1. Asegurar que solo el Paso 1 esté visible y ajustado en altura al inicio
    formSteps.forEach((s, i) => {
        if (i > 0) s.classList.remove('active');
    });
    adjustFormHeight(0); // Ajustar la altura inicial
    
    // 2. Ocultar botones de navegación que no aplican en el primer paso
    prevBtn.classList.add('hidden');
    submitBtn.classList.add('hidden');
});