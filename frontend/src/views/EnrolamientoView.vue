<template>
  <v-container class="py-6">
    <div class="text-h6 font-weight-bold mb-1">Enrolamiento facial</div>
    <div class="text-medium-emphasis text-body-2 mb-5">
      Seleccioná un socio y registrá las fotografías de su rostro para generar los vectores faciales
    </div>

    <v-row>
      <v-col cols="12" md="6">
        <v-card flat border class="mb-4">
          <v-card-text class="pa-4">
            <div class="text-caption text-medium-emphasis text-uppercase mb-2">Socio</div>
            <v-autocomplete
              v-model="selectedPerson"
              :items="socios"
              item-title="fullName"
              item-value="personId"
              label="Buscar socio por nombre"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-magnify"
              :loading="loadingSocios"
              clearable
              hide-no-data
            />
            <v-alert v-if="listError" type="error" variant="tonal" density="compact" class="mt-3" :text="listError" />
          </v-card-text>
        </v-card>

        <v-card flat border>
          <v-card-text class="pa-4">
            <template v-if="selectedSocio">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="font-weight-medium">{{ selectedSocio.nombre }} {{ selectedSocio.apellido }}</div>
                <v-chip size="small" variant="tonal" :color="membershipOk(selectedSocio) ? 'success' : 'error'">
                  {{ membershipLabel(selectedSocio) }}
                </v-chip>
              </div>
              <div class="text-body-2 text-medium-emphasis mb-1">{{ selectedSocio.email }}</div>
              <div class="text-body-2 text-medium-emphasis">
                DNI: {{ selectedSocio.dni || '—' }} · Vence {{ selectedSocio.membresia_hasta || '—' }}
              </div>
            </template>
            <v-alert v-else type="info" variant="tonal" density="compact">
              Buscá y seleccioná un socio para cargarle las fotos de su rostro.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card flat border>
          <v-card-text class="pa-4">
            <PhotoCapture ref="photoCaptureRef" v-model="photoB64s" />

            <v-alert v-if="uploadError" type="error" variant="tonal" density="compact" class="mt-3" :text="uploadError" />
            <v-alert v-if="uploadSuccess" type="success" variant="tonal" density="compact" class="mt-3" :text="uploadSuccess" />

            <v-btn
              block
              color="primary"
              variant="flat"
              class="mt-4"
              :loading="uploading"
              :disabled="!selectedPerson || photoB64s.length === 0"
              @click="handleUpload"
            >
              Procesar vectores faciales
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import PhotoCapture from '@/components/PhotoCapture.vue'

const route = useRoute()

const socios = ref([])
const loadingSocios = ref(false)
const listError = ref('')
const selectedPerson = ref(null)

const selectedSocio = computed(() => socios.value.find((p) => p.personId === selectedPerson.value) || null)

function membershipOk(p) {
  if (!p.membresia_hasta) return false
  return new Date(p.membresia_hasta) >= new Date(new Date().toDateString())
}

function membershipLabel(p) {
  if (!p.membresia_hasta) return 'Sin membresía'
  return membershipOk(p) ? 'Cuota al día' : 'Membresía vencida'
}

async function loadSocios() {
  loadingSocios.value = true
  listError.value = ''
  try {
    const response = await api.get('/persons')
    if (!response.ok) throw new Error('Error al cargar socios')
    socios.value = (await response.json()).map((p) => ({ ...p, fullName: `${p.nombre} ${p.apellido}` }))
  } catch (e) {
    listError.value = e.message
  } finally {
    loadingSocios.value = false
  }
}

onMounted(async () => {
  await loadSocios()
  if (route.query.personId) {
    selectedPerson.value = route.query.personId
  }
})

const photoCaptureRef = ref(null)
const photoB64s = ref([])
const uploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')

async function handleUpload() {
  uploadError.value = ''
  uploadSuccess.value = ''
  uploading.value = true
  try {
    if (!selectedSocio.value) {
      throw new Error('Seleccioná un socio')
    }
    const response = await api.post(`/persons/${selectedSocio.value.personId}/embeddings`, {
      images: photoB64s.value,
    })
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Error al subir las fotos')
    }
    const data = await response.json()
    uploadSuccess.value = `${selectedSocio.value.nombre} ${selectedSocio.value.apellido}: ${data.message}`
    photoB64s.value = []
    photoCaptureRef.value?.clear()
  } catch (e) {
    uploadError.value = e.message
  } finally {
    uploading.value = false
  }
}
</script>
