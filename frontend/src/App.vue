<script setup>
import { ref } from 'vue'
import axios from 'axios'

// ១. អថេរកំណត់ Tab ដែលកំពុងបើក
const activeTab = ref('text') // 'text', 'wifi', 'email'

// ២. អថេរផ្ទុកទិន្នន័យតាមប្រភេទនីមួយៗ
// --> សម្រាប់ Text/Link
const textInput = ref('https://google.com')

// --> សម្រាប់ Wi-Fi
const wifiSsid = ref('')
const wifiPassword = ref('')
const wifiEncryption = ref('WPA')
const wifiHidden = ref(false)

// --> សម្រាប់ Email
const emailAddress = ref('')
const emailSubject = ref('')
const emailBody = ref('')

// ៣. អថេរសម្រាប់ការកំណត់ទូទៅ (ពណ៌ និង Logo)
const fgColor = ref('#5b58c7') 
const bgColor = ref('#ffffff')
const logoFile = ref(null)
const qrImageUrl = ref(null)
const isLoading = ref(false)

// មុខងារ Logo
const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) logoFile.value = file
}

const removeLogo = () => {
  logoFile.value = null
  document.getElementById('logoInput').value = ''
}

// មុខងារផ្គុំទិន្នន័យទៅជាទម្រង់ QR ស្តង់ដារ
const getFormattedData = () => {
  if (activeTab.value === 'text') {
    return textInput.value
  } else if (activeTab.value === 'wifi') {
    const hidden = wifiHidden.value ? 'true' : 'false'
    return `WIFI:T:${wifiEncryption.value};S:${wifiSsid.value};P:${wifiPassword.value};H:${hidden};;`
  } else if (activeTab.value === 'email') {
    return `mailto:${emailAddress.value}?subject=${encodeURIComponent(emailSubject.value)}&body=${encodeURIComponent(emailBody.value)}`
  }
  return ''
}

// មុខងារហៅ API ទៅកាន់ Backend
const generateQR = async () => {
  const finalData = getFormattedData()
  
  if (!finalData) {
    alert("សូមបំពេញព័ត៌មានឲ្យបានគ្រប់គ្រាន់ជាមុនសិន!")
    return
  }
  
  isLoading.value = true

  try {
    const formData = new FormData()
    formData.append('text', finalData) // បញ្ជូនទិន្នន័យដែលបានផ្គុំរួច
    formData.append('type', activeTab.value)
    formData.append('fg_color', fgColor.value)
    formData.append('bg_color', bgColor.value)
    
    if (logoFile.value) {
      formData.append('logo', logoFile.value)
    }

    // ប្តូរ URL ទៅជា Link API ពិតប្រាកដរបស់អ្នកនៅលើ Render
    const response = await axios.post(`https://qr-code-generator-m7bj.onrender.com/api/generate`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    
    if (qrImageUrl.value) URL.revokeObjectURL(qrImageUrl.value)
    qrImageUrl.value = URL.createObjectURL(response.data)
    
  } catch (error) {
    console.error("មានបញ្ហា:", error)
    alert("មិនអាចបង្កើត QR Code បានទេ។ សូមពិនិត្យមើល Backend របស់អ្នក។")
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="app-wrapper">
    <header class="header">
      <div class="logo-area">
        <span class="icon">🔲</span>
        <h2>កូដQR</h2>
      </div>
    </header>

    <div class="main-container">
      
      <div class="left-panel">
        <div class="section">
          <h3>Choose Type</h3>
          <div class="tabs">
            <button class="tab" :class="{ active: activeTab === 'text' }" @click="activeTab = 'text'">📝 Text / Link</button>
            <button class="tab" :class="{ active: activeTab === 'wifi' }" @click="activeTab = 'wifi'">📶 Wi-Fi</button>
            <button class="tab" :class="{ active: activeTab === 'email' }" @click="activeTab = 'email'">📧 Email</button>
          </div>
        </div>

        <div v-if="activeTab === 'text'" class="section fade-in">
          <h3>Content</h3>
          <textarea v-model="textInput" rows="4" placeholder="បញ្ចូលអត្ថបទ ឬ URL នៅទីនេះ..."></textarea>
        </div>

        <div v-if="activeTab === 'wifi'" class="section fade-in">
          <h3>Wi-Fi Details</h3>
          <div class="form-group">
            <label>Network Name (SSID)</label>
            <input type="text" v-model="wifiSsid" placeholder="ឧ. MyHomeWiFi" />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" v-model="wifiPassword" placeholder="បញ្ចូលលេខសម្ងាត់" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Encryption</label>
              <select v-model="wifiEncryption">
                <option value="WPA">WPA/WPA2</option>
                <option value="WEP">WEP</option>
                <option value="nopass">គ្មានលេខសម្ងាត់ (None)</option>
              </select>
            </div>
            <div class="form-group checkbox-group">
              <label>
                <input type="checkbox" v-model="wifiHidden" /> 
                Hidden Network
              </label>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'email'" class="section fade-in">
          <h3>Email Details</h3>
          <div class="form-group">
            <label>Email To</label>
            <input type="email" v-model="emailAddress" placeholder="ឧ. hello@example.com" />
          </div>
          <div class="form-group">
            <label>Subject</label>
            <input type="text" v-model="emailSubject" placeholder="ប្រធានបទ..." />
          </div>
          <div class="form-group">
            <label>Message Body</label>
            <textarea v-model="emailBody" rows="3" placeholder="សរសេរសាររបស់អ្នកនៅទីនេះ..."></textarea>
          </div>
        </div>

        <div class="section">
          <h3>Set Logo</h3>
          <p class="subtitle">Logo នឹងត្រូវដាក់នៅចំកណ្តាល QR Code</p>
          <div class="upload-box">
            <input type="file" id="logoInput" accept="image/png, image/jpeg" @change="handleLogoUpload" />
            <span v-if="logoFile" class="file-name">
              {{ logoFile.name }}
              <button @click.prevent="removeLogo" class="remove-btn">❌</button>
            </span>
          </div>
        </div>
        
        <button class="generate-btn" @click="generateQR" :disabled="isLoading">
          {{ isLoading ? 'កំពុងបង្កើត...' : '🚀 បង្កើត QR Code ឥឡូវនេះ' }}
        </button>
      </div>

      <div class="right-panel">
        <div class="preview-card">
          <div class="preview-header">
            <h3>👁️ Show Result</h3>
            <a v-if="qrImageUrl" :href="qrImageUrl" download="my_qrcode.png" class="download-btn">⬇️ Download</a>
          </div>
          <div class="qr-display">
            <img v-if="qrImageUrl" :src="qrImageUrl" alt="QR Code" class="qr-image" />
            <div v-else class="placeholder">
              <p>សូមចុចប៊ូតុង "បង្កើត" ដើម្បីមើលលទ្ធផល</p>
            </div>
          </div>
        </div>

        <div class="color-settings-card">
          <h3>🎨 Color Settings</h3>
          <div class="color-row">
            <div class="color-picker-group">
              <label>Foreground</label>
              <input type="color" v-model="fgColor" />
            </div>
            <div class="color-picker-group">
              <label>Background</label>
              <input type="color" v-model="bgColor" />
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* រចនាប័ទ្មទូទៅ (រក្សាទុកភាគច្រើនដូចចាស់) */
.app-wrapper {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

.header {
  background: white;
  padding: 15px 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2b3a55;
  font-weight: bold;
}

.main-container {
  display: flex;
  max-width: 1200px;
  margin: 30px auto;
  gap: 30px;
  padding: 0 20px;
}

.left-panel {
  flex: 1.2;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.section {
  margin-bottom: 25px;
}

h3 {
  font-size: 16px;
  color: #2b3a55;
  margin-bottom: 15px;
}

.subtitle {
  font-size: 12px;
  color: #777;
  margin-top: -10px;
  margin-bottom: 10px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s;
}

.tab.active {
  background: #2b3a55;
  color: white;
  border-color: #2b3a55;
}

/* CSS ថ្មីសម្រាប់ទម្រង់បញ្ចូលទិន្នន័យ (Forms) */
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
  margin-top: 25px;
}

input[type="text"], input[type="password"], input[type="email"], select, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
}

.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ផ្នែកផ្សេងៗទៀតរក្សាដូចចាស់ */
.upload-box {
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px dashed #bbb;
  padding: 15px;
  border-radius: 8px;
}

.file-name {
  font-size: 14px;
  color: #4CAF50;
  font-weight: bold;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 10px;
}

.generate-btn {
  width: 100%;
  padding: 15px;
  background: #5b58c7;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
}

.generate-btn:hover { background: #4a47a3; }
.generate-btn:disabled { background: #ccc; }

.right-panel {
  flex: 0.8;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-card, .color-settings-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.download-btn {
  padding: 8px 15px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  text-decoration: none;
  color: #333;
  font-size: 14px;
}

.qr-display {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f4f6fa;
  border-radius: 8px;
  min-height: 300px;
  padding: 20px;
}

.qr-image {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.color-row { display: flex; gap: 30px; }
.color-picker-group { display: flex; flex-direction: column; gap: 10px; }
input[type="color"] { width: 100px; height: 40px; border: none; border-radius: 5px; cursor: pointer; }

@media (max-width: 768px) { .main-container { flex-direction: column; } }
</style>