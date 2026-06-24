<script setup>
import { ref } from 'vue'
import axios from 'axios'

// អថេរសម្រាប់ផ្ទុកទិន្នន័យ (State Variables)
const textInput = ref('https://google.com')
const fgColor = ref('#5b58c7') // ពណ៌ដើម (ពណ៌ស្វាយដូចក្នុងរូប)
const bgColor = ref('#ffffff') // ពណ៌ផ្ទៃខាងក្រោយ
const logoFile = ref(null)
const qrImageUrl = ref(null)
const isLoading = ref(false)

// ចាប់យករូបភាព Logo ពេលអ្នកប្រើប្រាស់ Upload
const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    logoFile.value = file
  }
}

// លុប Logo ចេញវិញ
const removeLogo = () => {
  logoFile.value = null
  document.getElementById('logoInput').value = '' // Reset input
}

// មុខងារហៅ API ទៅកាន់ Backend
const generateQR = async () => {
  if (!textInput.value) {
    alert("សូមបញ្ចូលអត្ថបទ ឬតំណភ្ជាប់ជាមុនសិន!")
    return
  }
  
  isLoading.value = true

  try {
    // ដោយសារយើងមាន File យើងត្រូវប្រើ FormData ជំនួស JSON ធម្មតា
    const formData = new FormData()
    formData.append('text', textInput.value)
    formData.append('type', 'text')
    formData.append('fg_color', fgColor.value)
    formData.append('bg_color', bgColor.value)
    
    if (logoFile.value) {
      formData.append('logo', logoFile.value)
    }

    // បាញ់ Request ទៅកាន់ API (ប្តូរ URL នេះទៅជា Link Render របស់អ្នកពេលដាក់ឲ្យប្រើប្រាស់ពិតប្រាកដ)
    const response = await axios.post(`https://qr-code-generator-m7bj.onrender.com/api/generate`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob' // ចង់បានទិន្នន័យជារូបភាព
    })
    
    // បង្កើត URL ពីរូបភាពដែលទទួលបាន
    if (qrImageUrl.value) URL.revokeObjectURL(qrImageUrl.value) // លុប Memory ចាស់
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
            <button class="tab active">📝 Text / Link</button>
            <button class="tab disabled">📶 Wi-Fi</button>
            <button class="tab disabled">📧 Email</button>
          </div>
        </div>

        <div class="section">
          <h3>Content</h3>
          <textarea 
            v-model="textInput" 
            rows="4" 
            placeholder="បញ្ចូលអត្ថបទ ឬ URL នៅទីនេះ..."
          ></textarea>
        </div>

        <div class="section">
          <h3>Set Logo</h3>
          <p class="subtitle">Logo នឹងត្រូវដាក់នៅចំកណ្តាល QR Code</p>
          <div class="upload-box">
            <input 
              type="file" 
              id="logoInput"
              accept="image/png, image/jpeg" 
              @change="handleLogoUpload"
            />
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
            <a v-if="qrImageUrl" :href="qrImageUrl" download="my_qrcode.png" class="download-btn">
              ⬇️ Download
            </a>
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
/* រចនាប័ទ្មទូទៅ */
.app-wrapper {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f6fa;
  min-height: 100vh;
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
}

.main-container {
  display: flex;
  max-width: 1200px;
  margin: 30px auto;
  gap: 30px;
  padding: 0 20px;
}

/* ផ្នែកខាងឆ្វេង */
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
}

.tab {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.tab.active {
  background: #2b3a55;
  color: white;
  border-color: #2b3a55;
}

.tab.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
  box-sizing: border-box;
}

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

.generate-btn:hover {
  background: #4a47a3;
}

.generate-btn:disabled {
  background: #ccc;
}

/* ផ្នែកខាងស្តាំ */
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

.download-btn:hover {
  background: #f4f6fa;
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
  height: auto;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.placeholder p {
  color: #888;
}

.color-row {
  display: flex;
  gap: 30px;
}

.color-picker-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input[type="color"] {
  width: 100px;
  height: 40px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

/* សម្រាប់អេក្រង់ទូរស័ព្ទ */
@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
}
</style>