<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import {
  createEquipmentComponentAssignment,
  getEquipmentComponentAssignments,
  getEquipmentComponents,
  updateEquipmentComponentAssignment,
} from "../../../services/equipment.service"

const props = defineProps({ equipmentId: { type: String, required: true } })
const assignments = ref([])
const components = ref([])
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const showArchived = ref(false)
const formOpen = ref(false)
const editingId = ref("")

const form = reactive({
  component: "", serial_number: "", status: "installed", position: "",
  installed_at: "", installation_meter: null, removed_at: "", removal_meter: null,
  removed_disposition: "not_applicable", reference_type: "manual", reference_id: null,
  installation_notes: "", removal_notes: "", is_active: true,
})
const activeComponents = computed(() => components.value.filter(x => !x.is_archived && x.is_active))
function normalizeList(r){ return Array.isArray(r) ? r : (r?.results || []) }
function localDateTime(v){ if(!v) return ""; const d=new Date(v); d.setMinutes(d.getMinutes()-d.getTimezoneOffset()); return d.toISOString().slice(0,16) }
function apiDateTime(v){ return v ? new Date(v).toISOString() : null }
function formatDate(v){ return v ? new Intl.DateTimeFormat("es-PE",{dateStyle:"medium",timeStyle:"short"}).format(new Date(v)) : "—" }
async function load(){ loading.value=true; errorMessage.value=""; try { const [a,c]=await Promise.all([getEquipmentComponentAssignments({equipment:props.equipmentId,includeArchived:showArchived.value}),getEquipmentComponents({isActive:true})]); assignments.value=normalizeList(a); components.value=normalizeList(c) } catch(e){ errorMessage.value=e.message } finally{loading.value=false} }
function reset(){ editingId.value=""; Object.assign(form,{component:"",serial_number:"",status:"installed",position:"",installed_at:localDateTime(new Date()),installation_meter:null,removed_at:"",removal_meter:null,removed_disposition:"not_applicable",reference_type:"manual",reference_id:null,installation_notes:"",removal_notes:"",is_active:true}) }
function openCreate(){ reset(); formOpen.value=true }
function openEdit(item){ editingId.value=item.id; Object.assign(form,{component:item.component||"",serial_number:item.serial_number||"",status:item.status||"installed",position:item.position||"",installed_at:localDateTime(item.installed_at),installation_meter:item.installation_meter??null,removed_at:localDateTime(item.removed_at),removal_meter:item.removal_meter??null,removed_disposition:item.removed_disposition||"not_applicable",reference_type:item.reference_type||"manual",reference_id:item.reference_id||null,installation_notes:item.installation_notes||"",removal_notes:item.removal_notes||"",is_active:Boolean(item.is_active)}); formOpen.value=true }
async function save(){ if(!form.component){errorMessage.value="Selecciona un componente.";return} saving.value=true; errorMessage.value=""; try { const payload={...form,equipment:props.equipmentId,serial_number:form.serial_number.trim(),position:form.position.trim(),installed_at:apiDateTime(form.installed_at),removed_at:apiDateTime(form.removed_at),installation_meter:form.installation_meter===""?null:form.installation_meter,removal_meter:form.removal_meter===""?null:form.removal_meter,reference_id:form.reference_id||null,installation_notes:form.installation_notes.trim(),removal_notes:form.removal_notes.trim()}; if(editingId.value) await updateEquipmentComponentAssignment(editingId.value,payload); else await createEquipmentComponentAssignment(payload); successMessage.value="Asignación guardada correctamente."; formOpen.value=false; await load() } catch(e){errorMessage.value=e.message} finally{saving.value=false} }
onMounted(load)
</script>

<template>
<section class="component-panel">
  <header class="panel-header"><div><h3>Componentes instalados</h3><p>Historial técnico por equipo, sin control de inventario.</p></div><button type="button" @click="openCreate">Agregar componente</button></header>
  <div class="toolbar"><label><input v-model="showArchived" type="checkbox" @change="load" /> Mostrar archivados</label><button type="button" @click="load">Actualizar</button></div>
  <p v-if="errorMessage" class="message error">{{ errorMessage }}</p><p v-if="successMessage" class="message success">{{ successMessage }}</p>
  <div v-if="loading" class="empty">Cargando componentes…</div>
  <div v-else-if="!assignments.length" class="empty">Este equipo todavía no tiene componentes asignados.</div>
  <div v-else class="table-wrap"><table><thead><tr><th>Componente</th><th>Serie</th><th>Posición</th><th>Estado</th><th>Instalación</th><th>Retiro</th><th></th></tr></thead><tbody><tr v-for="item in assignments" :key="item.id"><td><strong>{{ item.component_name }}</strong><small>{{ item.component_code }} · {{ item.component_type_name }}</small></td><td>{{ item.serial_number || "—" }}</td><td>{{ item.position || item.component_color_name || "—" }}</td><td>{{ item.status_name || item.status }}</td><td>{{ formatDate(item.installed_at) }}<small v-if="item.installation_meter">Contador: {{ item.installation_meter }}</small></td><td>{{ formatDate(item.removed_at) }}</td><td><button type="button" class="link" @click="openEdit(item)">Editar</button></td></tr></tbody></table></div>
  <Teleport to="body"><div v-if="formOpen" class="modal-backdrop" @click.self="formOpen=false"><form class="modal-card" @submit.prevent="save"><header><h3>{{ editingId ? "Editar asignación" : "Agregar componente" }}</h3><button type="button" @click="formOpen=false">×</button></header><div class="grid"><label class="full"><span>Componente *</span><select v-model="form.component" required><option value="">Selecciona</option><option v-for="item in activeComponents" :key="item.id" :value="item.id">{{ item.category_name }} · {{ item.name }} {{ item.color_name !== 'No aplica' ? `(${item.color_name})` : '' }}</option></select></label><label><span>Serie individual</span><input v-model="form.serial_number" /></label><label><span>Posición o color</span><input v-model="form.position" /></label><label><span>Estado</span><select v-model="form.status"><option value="reserved">Reservado</option><option value="delivered">Entregado</option><option value="installed">Instalado</option><option value="removed">Retirado</option><option value="returned">Devuelto</option><option value="discarded">Desechado</option><option value="cancelled">Cancelado</option></select></label><label><span>Fecha de instalación</span><input v-model="form.installed_at" type="datetime-local" /></label><label><span>Contador instalación</span><input v-model.number="form.installation_meter" type="number" min="0" /></label><label><span>Fecha de retiro</span><input v-model="form.removed_at" type="datetime-local" /></label><label><span>Contador retiro</span><input v-model.number="form.removal_meter" type="number" min="0" /></label><label><span>Destino retirado</span><select v-model="form.removed_disposition"><option value="not_applicable">No aplica</option><option value="send_to_repair">Enviar a reparación</option><option value="recoverable">Recuperable</option><option value="for_parts">Para partes</option><option value="discard">Desechar</option><option value="customer_return">Entregar al cliente</option></select></label><label class="full"><span>Notas de instalación</span><textarea v-model="form.installation_notes" rows="3"></textarea></label><label class="full"><span>Notas de retiro</span><textarea v-model="form.removal_notes" rows="3"></textarea></label><label class="check"><input v-model="form.is_active" type="checkbox" /><span>Continúa activo en el equipo</span></label></div><footer><button type="button" @click="formOpen=false">Cancelar</button><button type="submit" :disabled="saving">{{ saving ? "Guardando…" : "Guardar" }}</button></footer></form></div></Teleport>
</section>
</template>

<style scoped>
.component-panel{display:grid;gap:1rem}.panel-header,.toolbar{display:flex;align-items:center;justify-content:space-between;gap:1rem}.panel-header h3{margin:0}.panel-header p{margin:.25rem 0 0;color:#64748b}.panel-header button,.toolbar button,footer button{border:0;border-radius:10px;padding:.7rem 1rem;cursor:pointer}.panel-header>button,footer button[type=submit]{background:#1d4ed8;color:white}.table-wrap{overflow:auto;border:1px solid #e2e8f0;border-radius:14px}table{width:100%;border-collapse:collapse}th,td{padding:.8rem;text-align:left;border-bottom:1px solid #e2e8f0}td small{display:block;color:#64748b;margin-top:.2rem}.link{border:0;background:none;color:#1d4ed8;cursor:pointer}.empty{padding:2rem;text-align:center;color:#64748b}.message{padding:.75rem;border-radius:10px}.error{background:#fee2e2;color:#991b1b}.success{background:#dcfce7;color:#166534}.modal-backdrop{position:fixed;inset:0;background:#0f172a99;display:grid;place-items:center;padding:1rem;z-index:2000}.modal-card{background:white;border-radius:18px;width:min(850px,100%);max-height:92vh;overflow:auto;padding:1.2rem}.modal-card header,.modal-card footer{display:flex;justify-content:space-between;align-items:center;gap:1rem}.modal-card header button{border:0;background:none;font-size:1.5rem}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin:1rem 0}.grid label{display:grid;gap:.4rem}.grid input,.grid select,.grid textarea{border:1px solid #cbd5e1;border-radius:10px;padding:.7rem}.full{grid-column:1/-1}.check{display:flex!important;align-items:center}.modal-card footer{justify-content:flex-end}@media(max-width:700px){.grid{grid-template-columns:1fr}.full{grid-column:auto}.panel-header{align-items:flex-start;flex-direction:column}}
</style>
