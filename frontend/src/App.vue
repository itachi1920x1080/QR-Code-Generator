<script setup>
import { ref } from 'vue'
import axios from 'axios'

// បង្កើតអថេរសម្រាប់ផ្ទុកទិន្នន័យ
const textInput = ref('')
const qrImageUrl = ref(null)
const isLoading = ref(false)

// មុខងារសម្រាប់ហៅ API ទៅកាន់ Backend
const generateQR = async () => {
  if (!textInput.value) {
    alert("សូមបញ្ចូលអត្ថបទ ឬតំណភ្ជាប់ជាមុនសិន!")
    return
  }
  
  isLoading.value = true
  qrImageUrl.value = null // លុបរូបចាស់ចេញពេលកំពុង Load ថ្មី

  try {
    // បាញ់ Request ទៅកាន់ FastAPI Backend
    const response = await axios.get(`http://127.0.0.1:8000/api/generate`, {
      params: { text: textInput.value },
      responseType: 'blob' // សំខាន់៖ ប្រាប់ axios ថាយើងចង់បានទិន្នន័យជារូបភាព (File/Blob) មិនមែនជាអត្ថបទទេ
    })
    
    // បម្លែងទិន្នន័យ Blob ឲ្យទៅជា URL ដើម្បីអាចបង្ហាញក្នុង Tag <img> បាន
    qrImageUrl.value = URL.createObjectURL(response.data)
  } catch (error) {
    console.error("មានបញ្ហា:", error)
    alert("មិនអាចបង្កើត QR Code បានទេ។ សូមប្រាកដថា Backend របស់អ្នកកំពុងដំណើរការ។")
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="container">
    <h1>QR Code Generator</h1>
    <p>បញ្ចូលតំណភ្ជាប់ (URL) ឬអត្ថបទរបស់អ្នកនៅទីនេះ៖</p>
    
    <div class="input-group">
      <input 
        v-model="textInput" 
        type="text" 
        placeholder="ឧទាហរណ៍៖ https://google.com" 
        @keyup.enter="generateQR"
      />
      <button @click="generateQR" :disabled="isLoading">
        {{ isLoading ? 'កំពុងបង្កើត...' : 'បង្កើត QR Code' }}
      </button>
    </div>

    <div v-if="qrImageUrl" class="result">
      <h2>លទ្ធផលរបស់អ្នក៖</h2>
      <img :src="qrImageUrl" alt="Generated QR Code" />
      <br>
      <a :href="qrImageUrl" download="my_qrcode.png">ទាញយករូបភាព (Download)</a>
    </div>
  </div>
</template>

<style scoped>
/* កូដ CSS ងាយៗសម្រាប់តុបតែង UI */
.container {
  font-family: Arial, sans-serif;
  max-width: 500px;
  margin: 50px auto;
  text-align: center;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  background-color: #f9f9f9;
}
.input-group {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}
input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:disabled {
  background-color: #ccc;
}
.result {
  margin-top: 30px;
}
img {
  max-width: 200px;
  margin-bottom: 15px;
  border: 5px solid white;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
a {
  text-decoration: none;
  color: #007BFF;
  font-weight: bold;
}
</style>