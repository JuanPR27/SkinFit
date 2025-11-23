/**
 * script.js (VERSIÓN ACTUALIZADA)
 * Lógica de Navegación del Formulario Multi-paso y Ajuste de Dimensiones
 * Adaptado para la nueva estructura de rutina unificada
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
            // Se usa la altura del fieldset + 120px para el espacio de los botones y padding.
            const height = fieldset.offsetHeight + 120; 
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
        
        // Paso 1: Validar nombre y edad
        if (stepIndex === 0) {
            const nombreInput = step.querySelector('#nombre');
            const edadInput = step.querySelector('#edad');
            
            if (!nombreInput.value.trim()) {
                showFieldError(nombreInput, 'Por favor ingresa tu nombre');
                isValid = false;
            } else {
                clearFieldError(nombreInput);
            }
            
            if (!edadInput.value || edadInput.value < 10 || edadInput.value > 100) {
                showFieldError(edadInput, 'La edad debe estar entre 10 y 100 años');
                isValid = false;
            } else {
                clearFieldError(edadInput);
            }
        }
        
        // Paso 2: Validar tipo de piel
        if (stepIndex === 1) {
            const tipoPielSelect = step.querySelector('#tipo_piel');
            
            if (!tipoPielSelect.value) {
                showFieldError(tipoPielSelect, 'Por favor selecciona tu tipo de piel');
                isValid = false;
            } else {
                clearFieldError(tipoPielSelect);
            }
        }
        
        // Paso 3: Validar selección de rutina
        if (stepIndex === 2) {
            const rutinaOptions = step.querySelectorAll('input[name="frecuencia_rutina"]');
            let rutinaSelected = false;
            
            rutinaOptions.forEach(option => {
                if (option.checked) {
                    rutinaSelected = true;
                }
            });
            
            if (!rutinaSelected) {
                showStepError(step, 'Por favor selecciona un nivel de rutina');
                isValid = false;
            } else {
                clearStepError(step);
            }
        }
        
        return isValid;
    }

    /**
     * Muestra un error en un campo específico
     */
    function showFieldError(field, message) {
        // Remover error previo
        clearFieldError(field);
        
        // Aplicar estilos de error al campo
        field.classList.add('border-red-500', 'bg-red-50');
        
        // Crear elemento de error
        const errorElement = document.createElement('p');
        errorElement.className = 'text-red-500 text-xs mt-1 flex items-center';
        errorElement.innerHTML = `
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            ${message}
        `;
        
        // Insertar después del campo
        field.parentNode.appendChild(errorElement);
        field.dataset.hasError = 'true';
    }

    /**
     * Limpia el error de un campo
     */
    function clearFieldError(field) {
        field.classList.remove('border-red-500', 'bg-red-50');
        const errorElement = field.parentNode.querySelector('.text-red-500');
        if (errorElement) {
            errorElement.remove();
        }
        delete field.dataset.hasError;
    }

    /**
     * Muestra un error general en el paso
     */
    function showStepError(step, message) {
        // Remover error previo
        clearStepError(step);
        
        const errorElement = document.createElement('div');
        errorElement.className = 'bg-red-50 border border-red-200 rounded-lg p-3 mb-4';
        errorElement.innerHTML = `
            <p class="text-red-700 text-sm font-medium flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                ${message}
            </p>
        `;
        
        // Insertar al inicio del fieldset
        const fieldset = step.querySelector('fieldset');
        fieldset.insertBefore(errorElement, fieldset.firstChild);
    }

    /**
     * Limpia el error general del paso
     */
    function clearStepError(step) {
        const errorElement = step.querySelector('.bg-red-50');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Agrega interactividad a las tarjetas de opción de rutina
     */
    function initializeRoutineOptions() {
        const routineCards = document.querySelectorAll('.routine-option-card');
        
        routineCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remover selección de todas las tarjetas
                routineCards.forEach(c => {
                    c.querySelector('.routine-option-content').classList.remove('border-indigo-500', 'bg-indigo-50');
                });
                
                // Seleccionar esta tarjeta
                const content = this.querySelector('.routine-option-content');
                content.classList.add('border-indigo-500', 'bg-indigo-50');
                
                // Marcar el radio button
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
                
                // Limpiar cualquier error
                clearStepError(document.getElementById('step-3'));
            });
        });
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
        
        // 1. Limpiar animaciones previas
        prevStep.classList.remove('slide-out-left', 'slide-out-right', 'slide-in-left', 'slide-in-right');
        nextStep.classList.remove('slide-out-left', 'slide-out-right', 'slide-in-left', 'slide-in-right');
        
        // 2. Aplicar animaciones
        if (direction === 1) {
            // Avanzar: paso actual sale a la izquierda, nuevo entra desde la derecha
            prevStep.classList.add('slide-out-left');
            nextStep.classList.add('slide-in-right');
        } else {
            // Retroceder: paso actual sale a la derecha, nuevo entra desde la izquierda
            prevStep.classList.add('slide-out-right');
            nextStep.classList.add('slide-in-left');
        }
        
        // 3. Cambiar estados activos después de un breve delay
        setTimeout(() => {
            prevStep.classList.remove('active');
            nextStep.classList.add('active');
            
            // 4. Limpiar animaciones y ajustar altura
            setTimeout(() => {
                prevStep.classList.remove('slide-out-left', 'slide-out-right');
                nextStep.classList.remove('slide-in-left', 'slide-in-right');
                adjustFormHeight(newStepIndex);
                isAnimating = false;
            }, 50);
        }, 300);
        
        currentStep = newStepIndex;
        
        // 5. Actualizar visibilidad de los botones y el indicador
        updateNavigation();
        
        // 6. Asegurar que la vista se mantenga arriba
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Actualiza la visibilidad de los botones de navegación
     */
    function updateNavigation() {
        // Botón Anterior
        if (currentStep === 0) {
            prevBtn.classList.add('hidden');
        } else {
            prevBtn.classList.remove('hidden');
        }
        
        // Botones Siguiente/Enviar
        if (currentStep === totalSteps - 1) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
        
        // Actualizar indicador visual
        updateStepIndicator();
    }

    /**
     * Actualiza el indicador de pasos
     */
    function updateStepIndicator() {
        const dots = indicator.querySelectorAll('div');
        dots.forEach((dot, index) => {
            // Resetear todos los puntos
            dot.classList.remove('bg-pink-500', 'w-8', 'w-12', 'bg-gray-300');
            dot.classList.add('bg-gray-300', 'w-8');
            
            // Puntos completados
            if (index < currentStep) {
                dot.classList.remove('bg-gray-300');
                dot.classList.add('bg-pink-500', 'w-8');
            }
            
            // Punto actual
            if (index === currentStep) {
                dot.classList.remove('bg-gray-300', 'w-8');
                dot.classList.add('bg-pink-500', 'w-12');
            }
        });
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

    // Validación en tiempo real para campos de texto
    document.querySelectorAll('#nombre, #edad').forEach(input => {
        input.addEventListener('blur', function() {
            if (currentStep === 0) {
                validateStep(0);
            }
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });

    // Validación en tiempo real para select de tipo de piel
    document.querySelector('#tipo_piel').addEventListener('change', function() {
        clearFieldError(this);
    });

    // --- INICIALIZACIÓN ---
    
    function initializeForm() {
        // 1. Asegurar que solo el Paso 1 esté visible
        formSteps.forEach((step, index) => {
            if (index !== 0) {
                step.classList.remove('active');
            }
        });
        
        // 2. Ajustar la altura inicial
        adjustFormHeight(0);
        
        // 3. Inicializar navegación
        updateNavigation();
        
        // 4. Inicializar opciones de rutina
        initializeRoutineOptions();
        
        // 5. Agregar estilos de animación CSS dinámicamente
        addAnimationStyles();
    }

    /**
     * Agrega estilos CSS para las animaciones
     */
    function addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .form-step {
                transition: all 0.3s ease-in-out;
            }
            
            .slide-out-left {
                animation: slideOutLeft 0.3s ease-in-out forwards;
            }
            
            .slide-out-right {
                animation: slideOutRight 0.3s ease-in-out forwards;
            }
            
            .slide-in-right {
                animation: slideInRight 0.3s ease-in-out forwards;
            }
            
            .slide-in-left {
                animation: slideInLeft 0.3s ease-in-out forwards;
            }
            
            @keyframes slideOutLeft {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(-100%);
                }
            }
            
            @keyframes slideOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
            
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Inicializar el formulario cuando el DOM esté listo
    initializeForm();
});