<template>
  <div class="login-container">
    <div class="login-hero">
      <h1 class="hero-title">管理员控制台</h1>
      <p class="hero-subtitle">欢迎回来，请登录继续访问</p>
    </div>
    
    <div class="login-card">
      <div class="card-header">
        <h3>管理员登录</h3>
      </div>
      
      <div class="card-body">
        <div v-if="error" class="error-message">
          <i class="bi bi-exclamation-triangle-fill"></i>
          {{ error }}
        </div>
        
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username" class="form-label">用户名</label>
            <div class="input-group">
              <div class="input-prefix">
                <i class="bi bi-person-fill"></i>
              </div>
              <input 
                type="text" 
                class="custom-input" 
                id="username" 
                v-model="username" 
                required
                placeholder="请输入用户名"
                autocomplete="username"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="password" class="form-label">密码</label>
            <div class="input-group">
              <div class="input-prefix">
                <i class="bi bi-key-fill"></i>
              </div>
              <input 
                type="password" 
                class="custom-input" 
                id="password" 
                v-model="password" 
                required
                placeholder="请输入密码"
                autocomplete="current-password"
              >
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="btn-custom btn-primary login-btn" 
              :disabled="loading"
            >
              <div v-if="loading" class="spinner"></div>
              <span>{{ loading ? '登录中...' : '登录' }}</span>
            </button>
          </div>
        </form>
        
        <div class="login-info">
          <p>首次登录请使用</p>
          <div class="credentials">
            <div class="credential-item">
              <span class="credential-label">用户名:</span>
              <code>admin</code>
            </div>
            <div class="credential-item">
              <span class="credential-label">密码:</span>
              <code>admin123</code>
            </div>
          </div>
          <p class="info-note">首次登录后请立即修改密码</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const login = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // 使用FormData格式提交，因为这是OAuth2要求的格式
    const formData = new FormData()
    formData.append('username', username.value)
    formData.append('password', password.value)
    
    const response = await axios.post('/api/auth/token', formData)
    
    // 保存令牌到本地存储
    localStorage.setItem('accessToken', response.data.access_token)
    localStorage.setItem('tokenType', response.data.token_type)
    
    // 获取用户信息
    await checkUserInfo()
    
    // 发送登录成功事件，通知App.vue更新状态
    window.dispatchEvent(new Event('login-success'))
    
    // 登录成功后跳转
    router.push('/admin')
  } catch (err) {
    console.error('登录失败:', err)
    if (err.response && err.response.status === 401) {
      error.value = '用户名或密码不正确'
    } else {
      error.value = '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

const checkUserInfo = async () => {
  try {
    // 配置请求头携带令牌
    const token = localStorage.getItem('accessToken')
    const tokenType = localStorage.getItem('tokenType')
    
    if (!token) return
    
    const config = {
      headers: {
        'Authorization': `${tokenType} ${token}`
      }
    }
    
    // 获取当前用户信息
    const response = await axios.get('/api/auth/me', config)
    localStorage.setItem('user', JSON.stringify(response.data))
  } catch (err) {
    console.error('获取用户信息失败:', err)
    localStorage.removeItem('accessToken')
    localStorage.removeItem('tokenType')
    localStorage.removeItem('user')
  }
}
</script>

<style scoped>
/* 基础布局 */
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: calc(100vh - 120px);
  padding: 3rem 1rem;
}

/* 英雄区域 */
.login-hero {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  letter-spacing: -1px;
  text-shadow: 
    3px 3px 0 rgba(99, 102, 241, 0.2),
    6px 6px 10px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--gray-color);
  font-weight: 500;
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--card-radius);
  box-shadow: 
    0 15px 25px rgba(0, 0, 0, 0.1),
    inset 0 -2px 6px rgba(255, 255, 255, 0.7),
    inset 2px 2px 6px rgba(255, 255, 255, 1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: slideUp 0.5s ease-out;
  margin-bottom: 2rem;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 20px 30px rgba(0, 0, 0, 0.15),
    inset 0 -2px 6px rgba(255, 255, 255, 0.7),
    inset 2px 2px 6px rgba(255, 255, 255, 1);
}

/* 卡片头部 */
.card-header {
  padding: 1.5rem;
  text-align: center;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  background: linear-gradient(to right, rgba(99, 102, 241, 0.05), rgba(124, 58, 237, 0.1));
}

.card-header h3 {
  margin: 0;
  color: var(--primary-color);
  font-weight: 700;
  font-size: 1.6rem;
}

/* 卡片内容 */
.card-body {
  padding: 2rem;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--dark-color);
}

.input-group {
  display: flex;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: var(--border-radius);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.input-group:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.9);
}

.input-prefix {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  background-color: rgba(99, 102, 241, 0.05);
  color: var(--primary-color);
  border-right: 1px solid rgba(99, 102, 241, 0.1);
}

.input-prefix i {
  font-size: 1.2rem;
}

.custom-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  outline: none;
  background: transparent;
  color: var(--dark-color);
}

.custom-input::placeholder {
  color: rgba(99, 102, 241, 0.4);
}

/* 错误信息 */
.error-message {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
  padding: 1rem;
  border-radius: var(--border-radius);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

.error-message i {
  font-size: 1.2rem;
}

/* 登录操作 */
.form-actions {
  margin-top: 2rem;
}

.login-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 48px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 默认账号信息 */
.login-info {
  margin-top: 2rem;
  padding: 1.25rem;
  border-radius: var(--border-radius);
  background: rgba(99, 102, 241, 0.05);
  text-align: center;
  position: relative;
  border: 1px dashed rgba(99, 102, 241, 0.3);
}

.login-info p {
  margin-bottom: 1rem;
  color: var(--gray-color);
  font-size: 0.95rem;
}

.credentials {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.credential-item {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.credential-label {
  font-weight: 600;
  color: var(--gray-color);
}

code {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.info-note {
  color: var(--accent-color) !important;
  font-weight: 500;
  margin-top: 0.5rem;
}

/* 按钮样式 */
.btn-custom {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  border: none;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}

.btn-custom::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: 0.5s;
}

.btn-custom:hover::before {
  left: 100%;
}

.btn-custom:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.btn-custom:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
  10%, 90% { transform: translateX(-1px); }
  20%, 80% { transform: translateX(2px); }
  30%, 50%, 70% { transform: translateX(-4px); }
  40%, 60% { transform: translateX(4px); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 576px) {
  .login-card {
    padding: 1rem;
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
}
</style> 