<script setup>
import { ref } from 'vue'
import axios from 'axios'

const activeTab = ref('text') 
const textInput = ref('https://google.com')

const wifiSsid = ref('')
const wifiPassword = ref('')
const wifiEncryption = ref('WPA')
const wifiHidden = ref(false)

const emailAddress = ref('')
const emailSubject = ref('')
const emailBody = ref('')

// អថេរថ្មីសម្រាប់ UI កម្រិតខ្ពស់
const fgColor = ref('#6e69cc') 
const bgColor = ref('#ffffff')
const spaceValue = ref(50) // Space ពី 0 ដល់ 100
const imageSize = ref(768) // ទំហំរូបភាពលំនាំដើម

const logoFile = ref(null)
const qrImageUrl = ref(null)
const isLoading = ref(false)

// មុខងារប្តូរពណ៌ចុះឡើង (Swap Colors)
const swapColors = () => {
  const temp = fgColor.value
  fgColor.value = bgColor.value
  bgColor.value = temp
}

const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) logoFile.value = file
}

const removeLogo = () => {
  logoFile.value = null
  document.getElementById('logoInput').value = ''
}

const getFormattedData = () => {
  if (activeTab.value === 'text') return textInput.value
  if (activeTab.value === 'wifi') return `WIFI:T:${wifiEncryption.value};S:${wifiSsid.value};P:${wifiPassword.value};H:${wifiHidden.value ? 'true' : 'false'};;`
  if (activeTab.value === 'email') return `mailto:${emailAddress.value}?subject=${encodeURIComponent(emailSubject.value)}&body=${encodeURIComponent(emailBody.value)}`
  return ''
}

const generateQR = async () => {
  const finalData = getFormattedData()
  if (!finalData) { alert("សូមបំពេញព័ត៌មានឲ្យបានគ្រប់គ្រាន់!"); return }
  
  isLoading.value = true

  try {
    const formData = new FormData()
    formData.append('text', finalData)
    formData.append('type', activeTab.value)
    formData.append('fg_color', fgColor.value)
    formData.append('bg_color', bgColor.value)
    
    // បម្លែង % របស់ Space ទៅជាទំហំគែម (Border) របស់ QR ពី 0 ទៅ 10
    const borderValue = Math.floor((spaceValue.value / 100) * 10)
    formData.append('space', borderValue)
    formData.append('size', imageSize.value)
    
    if (logoFile.value) formData.append('logo', logoFile.value)

    const response = await axios.post(`https://qr-code-generator-m7bj.onrender.com/api/generate`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob'
    })
    
    if (qrImageUrl.value) URL.revokeObjectURL(qrImageUrl.value)
    qrImageUrl.value = URL.createObjectURL(response.data)
    
  } catch (error) {
    console.error("មានបញ្ហា:", error)
    alert("មិនអាចបង្កើត QR Code បានទេ។")
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
           <div class="form-group"><label>Network Name (SSID)</label><input type="text" v-model="wifiSsid" /></div>
           <div class="form-group"><label>Password</label><input type="password" v-model="wifiPassword" /></div>
        </div>
        <div v-if="activeTab === 'email'" class="section fade-in">
           <div class="form-group"><label>Email To</label><input type="email" v-model="emailAddress" /></div>
        </div>

        <div class="section">
          <h3>Set Logo</h3>
          <div class="upload-box">
            <input type="file" id="logoInput" accept="image/png, image/jpeg" @change="handleLogoUpload" />
            <span v-if="logoFile" class="file-name">{{ logoFile.name }} <button @click.prevent="removeLogo" class="remove-btn">❌</button></span>
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
            <div v-else class="placeholder"><p>សូមចុចប៊ូតុង "បង្កើត" ដើម្បីមើលលទ្ធផល</p></div>
          </div>
        </div>

        <div class="advanced-settings-card">
          
          <div class="setting-group">
            <div class="setting-header">
              <h3>🎨 Color</h3>
              <div class="color-swatch-area">
                <button class="swap-btn" @click="swapColors">⇄</button>
                <div class="color-preview" :style="{ backgroundColor: fgColor }"></div>
                <div class="color-preview bordered" :style="{ backgroundColor: bgColor }"></div>
              </div>
            </div>
            <div class="color-inputs">
              <div class="hex-input-box">
                <input type="color" v-model="fgColor" class="hidden-color-picker">
                <input type="text" v-model="fgColor" class="hex-text">
              </div>
              <div class="hex-input-box">
                <input type="color" v-model="bgColor" class="hidden-color-picker">
                <input type="text" v-model="bgColor" class="hex-text">
              </div>
            </div>
          </div>

          <div class="setting-group border-top">
            <h3>🔲 Space</h3>
            <input type="range" min="0" max="100" v-model="spaceValue" class="custom-slider">
            <div class="slider-labels">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>

          <div class="setting-group border-top size-section">
            <h3 class="inline-h3">🖼️ Image Size</h3>
            <select v-model="imageSize" class="size-dropdown">
              <option value="512">512×512</option>
              <option value="768">768×768</option>
              <option value="1024">1024×1024</option>
              <option value="2048">2048×2048</option>
            </select>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* រចនាប័ទ្មចាស់ៗរក្សាដដែល */
.app-wrapper { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
.header { background: white; padding: 15px 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.logo-area { display: flex; align-items: center; gap: 10px; color: #2b3a55; font-weight: bold; }
.main-container { display: flex; max-width: 1200px; margin: 30px auto; gap: 30px; padding: 0 20px; }
.left-panel { flex: 1.2; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.section { margin-bottom: 25px; }
h3 { font-size: 16px; color: #2b3a55; margin-bottom: 15px; }
.tabs { display: flex; gap: 10px; margin-bottom: 20px; }
.tab { padding: 10px 20px; border: 1px solid #ddd; background: white; border-radius: 8px; cursor: pointer; font-weight: bold; }
.tab.active { background: #2b3a55; color: white; border-color: #2b3a55; }
.form-group { margin-bottom: 15px; display: flex; flex-direction: column; gap: 5px; }
input[type="text"], input[type="password"], input[type="email"], textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
.upload-box { display: flex; align-items: center; gap: 15px; border: 1px dashed #bbb; padding: 15px; border-radius: 8px; }
.generate-btn { width: 100%; padding: 15px; background: #5b58c7; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
.right-panel { flex: 0.8; display: flex; flex-direction: column; gap: 20px; }
.preview-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.download-btn { padding: 8px 15px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; }
.qr-display { display: flex; justify-content: center; align-items: center; background: #f4f6fa; border-radius: 8px; min-height: 300px; padding: 20px; }
.qr-image { max-width: 100%; border-radius: 8px; }

/* CSS ថ្មីសម្រាប់ UI របស់ Settings (Color, Space, Size) */
.advanced-settings-card {
  background: white;
  padding: 20px 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.setting-group { padding: 15px 0; }
.border-top { border-top: 1px solid #f0f0f0; }

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.color-swatch-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.swap-btn {
  background: none; border: none; cursor: pointer; font-size: 18px; color: #666;
}

.color-preview {
  width: 24px; height: 24px; border-radius: 4px;
}
.bordered { border: 1px solid #ddd; }

.color-inputs {
  display: flex; gap: 15px;
}

.hex-input-box {
  flex: 1;
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 5px 10px;
  position: relative;
}

.hidden-color-picker {
  opacity: 0; position: absolute; width: 100%; height: 100%; cursor: pointer;
}

.hex-text {
  border: none !important; padding: 5px !important; color: #555; font-weight: 500; font-family: monospace; pointer-events: none;
}

/* តុបតែង Slider (Space) */
.custom-slider {
  width: 100%; margin-top: 10px; cursor: pointer;
}
.slider-labels {
  display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-top: 5px; font-weight: bold;
}

/* តុបតែង Image Size */
.size-section {
  display: flex; align-items: center; gap: 20px;
}
.inline-h3 { margin: 0; }
.size-dropdown {
  background: #f0f2f5; border: none; padding: 8px 15px; border-radius: 20px; font-weight: bold; color: #333; outline: none; cursor: pointer;
}

@media (max-width: 768px) { .main-container { flex-direction: column; } }
</style>