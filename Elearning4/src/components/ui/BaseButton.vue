<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="loading-spinner"></span>
    <slot v-else></slot>
  </button>
</template>

<script>
export default {
  name: 'BaseButton',
  emits: ['click'],
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'danger', 'success', 'outline'].includes(value)
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    buttonClasses() {
      return [
        'base-button',
        `base-button--${this.variant}`,
        `base-button--${this.size}`,
        {
          'base-button--disabled': this.disabled,
          'base-button--loading': this.loading
        }
      ]
    }
  }
}
</script>

<style scoped>
.base-button {
  @apply font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.base-button--small {
  @apply px-3 py-1.5 text-sm;
}

.base-button--medium {
  @apply px-4 py-2 text-base;
}

.base-button--large {
  @apply px-6 py-3 text-lg;
}

.base-button--primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500;
}

.base-button--secondary {
  @apply bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500;
}

.base-button--danger {
  @apply bg-red-600 text-white hover:bg-red-700 focus:ring-red-500;
}

.base-button--success {
  @apply bg-green-600 text-white hover:bg-green-700 focus:ring-green-500;
}

.base-button--outline {
  @apply border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-gray-500;
}

.base-button--disabled {
  @apply opacity-50 cursor-not-allowed;
}

.loading-spinner {
  @apply inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin;
}
</style>