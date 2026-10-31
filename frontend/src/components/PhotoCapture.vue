<template>
  <div>
    <div class="text-caption text-medium-emphasis text-uppercase mb-2">Fotografías de rostro</div>

    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-3" :text="error" />

    <div v-if="stage === 'idle'" class="d-flex flex-column align-center py-6">
      <v-icon size="40" color="medium-emphasis" class="mb-3">mdi-camera-outline</v-icon>
      <div class="text-body-2 text-medium-emphasis mb-2 text-center">
        Activá la cámara o subí fotos para registrar el rostro
      </div>
    </div>

    <div v-show="stage === 'camera' || stage === 'preview'">
      <video
        v-show="stage === 'camera'"
        ref="videoRef"
        autoplay
        playsinline
        muted
        class="photo-capture-media"
      />
      <img v-if="stage === 'preview' && capturedImage" :src="capturedImage" class="photo-capture-media" />
    </div>
    <canvas ref="canvasRef" style="display: none" />

    <div class="d-flex mt-3 flex-wrap" style="gap: 8px">
      <v-btn v-if="stage === 'idle'" color="primary" variant="flat" @click="startCamera">
        Activar cámara
      </v-btn>
      <v-btn v-if="stage === 'camera'" color="primary" variant="flat" @click="takePhoto">
        Tomar foto
      </v-btn>
      <template v-if="stage === 'preview'">
        <v-btn variant="tonal" @click="retake">Volver a sacar foto</v-btn>
        <v-btn color="secondary" variant="flat" @click="addToPending">Agregar a la lista</v-btn>
      </template>
    </div>

    <template v-if="photos.length">
      <div class="text-caption text-medium-emphasis text-uppercase mt-4 mb-2">
        {{ photos.length }} foto{{ photos.length !== 1 ? 's' : '' }} lista{{ photos.length !== 1 ? 's' : '' }} para subir
      </div>
      <div class="d-flex flex-wrap mb-3" style="gap: 8px">
        <div v-for="(p, i) in photos" :key="i" class="photo-capture-thumb">
          <img :src="p.preview" />
          <v-btn icon size="x-small" variant="flat" color="error" class="photo-capture-thumb-remove" @click="removePhoto(i)">
            <v-icon size="14">mdi-close</v-icon>
          </v-btn>
        </div>
      </div>
    </template>

    <v-file-input
      v-model="fileInput"
      label="O elegí fotos desde el dispositivo"
      accept="image/*"
      variant="outlined"
      density="comfortable"
      prepend-icon=""
      prepend-inner-icon="mdi-image-outline"
      multiple
      :clearable="false"
    />
  </div>
</template>

<script setup>
import { nextTick, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const videoRef = ref(null)
const canvasRef = ref(null)
let stream = null

const stage = ref('idle') // idle | camera | preview
const capturedImage = ref('')
const fileInput = ref([])

const photos = ref([])
const error = ref('')

async function startCamera() {
  capturedImage.value = ''
  error.value = ''
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    stage.value = 'camera'
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (e) {
    error.value = 'No se pudo acceder a la cámara. Revisá los permisos del navegador.'
  }
}

function takePhoto() {
  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  capturedImage.value = canvas.toDataURL('image/jpeg')
  stage.value = 'preview'
}

function retake() {
  capturedImage.value = ''
  stage.value = 'camera'
}

function addToPending() {
  photos.value.push({
    base64: capturedImage.value.split(',')[1],
    preview: capturedImage.value,
  })
  emitChanges()
  capturedImage.value = ''
  stage.value = 'camera'
}

function removePhoto(index) {
  photos.value.splice(index, 1)
  emitChanges()
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop())
    stream = null
  }
}

function emitChanges() {
  emit('update:modelValue', photos.value.map((p) => p.base64))
  if (fileInput.value && fileInput.value.length) {
    const toBase64 = (file) => new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result.split(',')[1])
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
    Promise.all(fileInput.value.map(toBase64)).then((b64s) => {
      b64s.forEach((b) => {
        if (!photos.value.some((p) => p.base64 === b)) {
          photos.value.push({ base64: b, preview: `data:image/jpeg;base64,${b}` })
        }
      })
      emit('update:modelValue', photos.value.map((p) => p.base64))
    })
    fileInput.value = []
  }
}

function clear() {
  photos.value = []
  capturedImage.value = ''
  fileInput.value = []
  stage.value = 'idle'
  emit('update:modelValue', [])
}

defineExpose({ clear })

watch(
  () => props.modelValue,
  (val) => {
    if (val.length === 0 && photos.value.length > 0) {
      photos.value = []
      stage.value = 'idle'
    }
  },
)

onUnmounted(stopCamera)
</script>

<style scoped>
.photo-capture-media {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px;
  background: #000;
}
.photo-capture-thumb {
  position: relative;
  width: 64px;
  height: 64px;
}
.photo-capture-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}
.photo-capture-thumb-remove {
  position: absolute;
  top: -6px;
  right: -6px;
}
</style>
