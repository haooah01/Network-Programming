import { ref, reactive, computed } from 'vue'

export function useForm(initialData = {}, validationRules = {}) {
  const formData = reactive({ ...initialData })
  const errors = ref({})
  const isSubmitting = ref(false)

  const validate = () => {
    errors.value = {}
    let isValid = true

    for (const [field, rules] of Object.entries(validationRules)) {
      const value = formData[field]
      
      for (const rule of rules) {
        if (typeof rule === 'function') {
          const result = rule(value)
          if (result !== true) {
            errors.value[field] = result
            isValid = false
            break
          }
        }
      }
    }

    return isValid
  }

  const reset = () => {
    Object.assign(formData, initialData)
    errors.value = {}
    isSubmitting.value = false
  }

  const setField = (field, value) => {
    formData[field] = value
    if (errors.value[field]) {
      delete errors.value[field]
    }
  }

  const handleSubmit = async (submitFn) => {
    if (!validate()) return

    try {
      isSubmitting.value = true
      await submitFn(formData)
    } catch (error) {
      console.error('Form submission error:', error)
      throw error
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    formData,
    errors: computed(() => errors.value),
    isSubmitting: computed(() => isSubmitting.value),
    isValid: computed(() => Object.keys(errors.value).length === 0),
    validate,
    reset,
    setField,
    handleSubmit
  }
}

// Common validation rules
export const validationRules = {
  required: (value) => !!value || 'This field is required',
  email: (value) => {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailPattern.test(value) || 'Invalid email format'
  },
  minLength: (min) => (value) => 
    (value && value.length >= min) || `Minimum ${min} characters required`,
  maxLength: (max) => (value) => 
    (value && value.length <= max) || `Maximum ${max} characters allowed`,
  phone: (value) => {
    const phonePattern = /^\+?[\d\s-()]+$/
    return phonePattern.test(value) || 'Invalid phone number format'
  }
}