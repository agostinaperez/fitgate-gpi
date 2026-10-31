<template>
  <v-container class="py-6">
    <div class="d-flex align-center justify-space-between mb-1">
      <div>
        <div class="text-h6 font-weight-bold">Gestión de socios</div>
        <div class="text-medium-emphasis text-body-2">
          Registro y administración de personas para el reconocimiento facial
        </div>
      </div>
      <v-btn color="grey-darken-4" variant="flat" prepend-icon="mdi-account-plus" @click="openDialog">
        Registrar socio
      </v-btn>
    </div>

    <v-alert v-if="listError" type="error" variant="tonal" density="compact" class="mt-3" :text="listError" />

    <v-card flat border class="mt-4">
      <v-table>
        <thead>
          <tr>
            <th class="text-medium-emphasis text-caption">Socio</th>
            <th class="text-medium-emphasis text-caption">DNI</th>
            <th class="text-medium-emphasis text-caption">Estado</th>
            <th class="text-medium-emphasis text-caption text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in socios" :key="p.personId">
            <td>
              <div class="d-flex align-center">
                <v-avatar color="primary" size="40" class="mr-3">
                  <span class="text-white">{{ initials(p) }}</span>
                </v-avatar>
                <div>
                  <div class="text-body-1 font-weight-medium">{{ p.nombre }} {{ p.apellido }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ p.email }}</div>
                </div>
              </div>
            </td>
            <td class="text-body-2">{{ p.dni || '—' }}</td>
            <td>
              <div class="d-flex align-center" style="gap: 6px">
                <v-chip
                  size="small"
                  variant="tonal"
                  :color="membershipOk(p) ? 'success' : 'error'"
                >
                  {{ membershipLabel(p) }}
                </v-chip>
                <v-chip
                  size="small"
                  variant="tonal"
                  :color="p.activo ? 'primary' : 'error'"
                >
                  {{ p.activo ? 'Activo' : 'Inactivo' }}
                </v-chip>
              </div>
            </td>
            <td class="text-right">
              <v-btn
                icon
                variant="text"
                size="small"
                color="primary"
                :to="{ name: 'enrolamiento', query: { personId: p.personId } }"
                title="Gestionar fotografías"
              >
                <v-icon size="18">mdi-camera-plus</v-icon>
              </v-btn>
              <v-btn
                icon
                variant="text"
                size="small"
                color="error"
                :loading="deletingId === p.personId"
                @click="removePerson(p)"
                title="Borrar"
              >
                <v-icon size="18">mdi-delete-outline</v-icon>
              </v-btn>
            </td>
          </tr>
          <tr v-if="!loading && socios.length === 0">
            <td colspan="4" class="text-center text-medium-emphasis py-6">
              No hay socios registrados todavía.
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="640px">
      <v-card flat>
        <v-card-title class="text-h6 font-weight-bold">Registrar socio</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submit">
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field v-model="form.nombre" label="Nombre" variant="outlined" density="comfortable" required />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="form.apellido" label="Apellido" variant="outlined" density="comfortable" required />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="form.email" label="Email" type="email" variant="outlined" density="comfortable" required />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="form.dni" label="DNI" variant="outlined" density="comfortable" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="form.telefono" label="Teléfono" variant="outlined" density="comfortable" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.membresia_hasta"
                  label="Vencimiento de cuota"
                  type="date"
                  variant="outlined"
                  density="comfortable"
                  :clearable="true"
                />
              </v-col>
              <v-col cols="12">
                <v-switch v-model="form.activo" label="Cuenta activa" color="primary" inset hide-details />
              </v-col>
            </v-row>

            <v-divider class="my-4" />

            <PhotoCapture ref="photoCaptureRef" v-model="photos" />

            <v-alert v-if="submitError" type="error" variant="tonal" density="compact" class="mt-3" :text="submitError" />
          </v-form>
        </v-card-text>
        <v-card-actions class="px-4 pb-4">
          <v-btn variant="text" @click="dialog = false">Cancelar</v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="flat"
            :loading="saving"
            :disabled="!form.nombre || !form.apellido || !form.email || photos.length === 0"
            @click="submit"
          >
            Registrar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '@/services/api'
import PhotoCapture from '@/components/PhotoCapture.vue'

const socios = ref([])
const loading = ref(false)
const listError = ref('')
const deletingId = ref(null)

const dialog = ref(false)
const saving = ref(false)
const submitError = ref('')
const photos = ref([])
const photoCaptureRef = ref(null)

const form = reactive({
  nombre: '',
  apellido: '',
  email: '',
  dni: '',
  telefono: '',
  membresia_hasta: '',
  activo: true,
})

function initials(p) {
  return `${(p.nombre || '').charAt(0)}${(p.apellido || '').charAt(0)}`.toUpperCase()
}

function membershipOk(p) {
  if (!p.membresia_hasta) return false
  return new Date(p.membresia_hasta) >= new Date(new Date().toDateString())
}

function membershipLabel(p) {
  if (!p.membresia_hasta) return 'Sin membresía'
  return membershipOk(p) ? 'Cuota al día' : 'Membresía vencida'
}

async function loadSocios() {
  loading.value = true
  listError.value = ''
  try {
    const response = await api.get('/persons')
    if (!response.ok) throw new Error('Error al cargar socios')
    socios.value = await response.json()
  } catch (e) {
    listError.value = e.message
  } finally {
    loading.value = false
  }
}

function openDialog() {
  Object.assign(form, {
    nombre: '',
    apellido: '',
    email: '',
    dni: '',
    telefono: '',
    membresia_hasta: '',
    activo: true,
  })
  photos.value = []
  submitError.value = ''
  dialog.value = true
}

async function submit() {
  submitError.value = ''
  saving.value = true
  try {
    const body = {
      nombre: form.nombre,
      apellido: form.apellido,
      email: form.email,
      dni: form.dni || null,
      telefono: form.telefono || null,
      activo: form.activo,
      membresia_hasta: form.membresia_hasta || null,
    }

    const createResponse = await api.post('/persons', body)
    const person = await createResponse.json()
    if (!createResponse.ok) {
      throw new Error(person.detail || 'Error al registrar el socio')
    }

    if (photos.value.length > 0) {
      const embedResponse = await api.post(`/persons/${person.personId}/embeddings`, {
        images: photos.value,
      })
      if (!embedResponse.ok) {
        const data = await embedResponse.json()
        throw new Error(data.detail || 'Error al procesar las fotografías')
      }
    }

    dialog.value = false
    photoCaptureRef.value?.clear()
    await loadSocios()
  } catch (e) {
    submitError.value = e.message
  } finally {
    saving.value = false
  }
}

async function removePerson(p) {
  deletingId.value = p.personId
  listError.value = ''
  try {
    const response = await api.delete(`/persons/${p.personId}`)
    if (!response.ok) throw new Error('Error al borrar el socio')
    await loadSocios()
  } catch (e) {
    listError.value = e.message
  } finally {
    deletingId.value = null
  }
}

onMounted(loadSocios)
</script>
