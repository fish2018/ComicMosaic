import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { setupAxiosInterceptors } from './utils/auth'

// 配置axios基础URL
axios.defaults.baseURL = '/api'

// 设置请求拦截器
setupAxiosInterceptors()

const app = createApp(App)
app.use(router)
app.mount('#app') 