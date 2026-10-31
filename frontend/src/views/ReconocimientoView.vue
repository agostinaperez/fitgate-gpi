<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5">
        <div class="text-center mb-6">
          <v-icon size="48" color="primary" class="mb-3">mdi-face-recognition</v-icon>
          <div class="text-h5 font-weight-bold">Reconocimiento facial</div>
          <div class="text-body-2 text-medium-emphasis">
            Capturá un rostro para identificarlo contra los socios enrolados
          </div>
        </div>

        <v-card flat border class="pa-2">
          <v-card-text>
            <div v-if="stage === 'idle'" class="d-flex flex-column align-center py-6">
              <v-icon size="40" color="medium-emphasis" class="mb-3">mdi-camera-outline</v-icon>
              <div class="text-body-2 text-medium-emphasis mb-2 text-center">
                Activá la cámara para capturar un rostro
              </div>
            </div>

            <div v-show="stage === 'camera' || stage === 'preview' || stage === 'loading'">
              <video
                v-show="stage === 'camera'"
                ref="videoRef"
                autoplay
                playsinline
                muted
                class="recon-media"
              />
              <img v-if="stage !== 'camera' && capturedImage" :src="capturedImage" class="recon-media" />
            </div>
            <canvas ref="canvasRef" style="display: none" />

            <v-alert
              v-if="result"
              class="mt-4"
              :type="result.personId ? 'success' : 'warning'"
              variant="tonal"
              density="comfortable"
            >
              <div class="text-h6 font-weight-bold mt-2">
                {{ result.personId ? `${result.nombre} ${result.apellido}` : 'No reconocido' }}
              </div>
              <div class="text-body-2">
                {{ result.personId ? `Coincidencia con confianza ${confidencePct}` : 'El rostro no coincide con ningún socio enrolado.' }}
              </div>
            </v-alert>

            <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mt-4" :text="error" />
          </v-card-text>
          <v-card-actions class="px-4 pb-4">
            <v-btn v-if="stage === 'idle'" block color="primary" variant="flat" size="large" @click="startCamera">
              Activar cámara
            </v-btn>
            <v-btn v-else-if="stage === 'camera'" block color="primary" variant="flat" size="large" @click="takePhoto">
              Tomar foto
            </v-btn>
            <template v-else-if="stage === 'preview'">
              <v-btn variant="tonal" @click="retake">Volver a capturar</v-btn>
              <v-spacer />
              <v-btn color="primary" variant="flat" @click="recognize">Identificar rostro</v-btn>
            </template>
            <v-btn v-else-if="stage === 'loading'" block color="primary" variant="flat" size="large" loading disabled>
              Procesando...
            </v-btn>
          </v-card-actions>
        </v-card>

        <div class="text-center mt-6">
          <v-btn variant="text" size="small" @click="resetAll">
            <v-icon start size="16">mdi-refresh</v-icon>
            Reiniciar
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref } from 'vue'
import { api } from '@/services/api'

const videoRef = ref(null)
const canvasRef = ref(null)
let stream = null

const stage = ref('idle') // idle | camera | preview | loading
const capturedImage = ref('')
const result = ref(null)
const error = ref('')

const confidencePct = computed(() => `${Math.round((result.value?.confidence || 0) * 100)}%`)

async function startCamera() {
  error.value = ''
  result.value = null
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
  result.value = null
  error.value = ''
  stage.value = 'camera'
}

async function recognize() {
  error.value = ''
  result.value = null
  stage.value = 'loading'
  try {
    const base64 = capturedImage.value.split(',')[1]
    const response = await api.post('/face-recognition', { image: base64, threshold: 0.8 })
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || 'Error al procesar el rostro')
    }
    result.value = await response.json()
    // Emulación de la acción física de acceso mediante salida de logs en consola.
    console.log('[FitGate] Reconocimiento:', result.value)
    stopCamera()
    stage.value = 'preview'
  } catch (e) {
    error.value = e.message
    stage.value = 'preview'
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop())
    stream = null
  }
}

function resetAll() {
  stopCamera()
  capturedImage.value = ''
  result.value = null
  error.value = ''
  stage.value = 'idle'
}

onUnmounted(stopCamera)
</script>

<style scoped>
.recon-media {
  width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 8px;
  background: #000;
}
</style>
