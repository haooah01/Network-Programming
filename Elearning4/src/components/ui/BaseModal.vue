<template>
  <div
    v-if="show"
    class="modal-overlay"
    @click="handleOverlayClick"
  >
    <div
      class="modal-container"
      :class="sizeClasses"
      @click.stop
    >
      <div class="modal-header" v-if="$slots.header || title">
        <slot name="header">
          <h3 class="modal-title">{{ title }}</h3>
        </slot>
        <button
          v-if="showCloseButton"
          class="modal-close"
          @click="close"
        >
          ×
        </button>
      </div>

      <div class="modal-body">
        <slot></slot>
      </div>

      <div class="modal-footer" v-if="$slots.footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseModal',
  emits: ['close'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large', 'full'].includes(value)
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    },
    showCloseButton: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    sizeClasses() {
      return `modal-container--${this.size}`
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    handleOverlayClick() {
      if (this.closeOnOverlay) {
        this.close()
      }
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = 'auto'
      }
    }
  },
  beforeUnmount() {
    document.body.style.overflow = 'auto'
  }
}
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50;
}

.modal-container {
  @apply bg-white rounded-lg shadow-xl max-h-screen overflow-hidden;
}

.modal-container--small {
  @apply w-full max-w-sm mx-4;
}

.modal-container--medium {
  @apply w-full max-w-md mx-4;
}

.modal-container--large {
  @apply w-full max-w-2xl mx-4;
}

.modal-container--full {
  @apply w-full h-full max-w-none mx-0 rounded-none;
}

.modal-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.modal-title {
  @apply text-lg font-semibold text-gray-900;
}

.modal-close {
  @apply text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center;
}

.modal-body {
  @apply p-6 overflow-y-auto;
}

.modal-footer {
  @apply px-6 py-4 bg-gray-50 border-t border-gray-200;
}
</style>