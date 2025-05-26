<template>
  <div class="submit-resource">
    <div class="hero-section">
      <h1 class="hero-title">{{ isSupplementMode ? '补充资源' : '提交资源' }}</h1>
      <p class="hero-subtitle">{{ isSupplementMode ? '为现有资源添加新图片和链接' : '分享您喜爱的优质资源，让更多人受益' }}</p>
    </div>
    
    <div v-if="submitting" class="loading-container">
      <div class="loader"></div>
      <p>正在提交资源，请稍候...</p>
    </div>
    
    <div v-else-if="submitSuccess" class="success-card fade-in">
      <div class="success-icon">
        <i class="bi bi-check-circle-fill"></i>
      </div>
      <h3>提交成功!</h3>
      <p>您的资源已成功提交到平台，正在等待管理员审批。</p>
      <p>审批通过后，资源将出现在首页列表中。</p>
      <div class="success-actions">
        <router-link to="/" class="btn-custom btn-outline">返回首页</router-link>
        <button @click="resetForm" class="btn-custom btn-primary">继续提交</button>
      </div>
    </div>
    
    <form v-else @submit.prevent="submitResource" class="form-card">
      <!-- 提交说明 -->
      <div class="info-banner">
        <i class="bi bi-info-circle"></i>
        <span>{{ isSupplementMode ? '您正在进行资源补充，审核通过后将添加到已有资源。' : '您正在提交新资源，审核通过后将显示在首页。' }}</span>
      </div>
      
      <!-- 资源标题搜索区域 -->
      <div class="search-card" v-if="!isSupplementMode">
        <div class="card-header">
          <h3>检查资源是否存在</h3>
        </div>
        <div class="card-body">
          <p class="text-note">请先搜索资源标题，检查是否已存在以避免重复提交：</p>
          <div v-if="isFromDetailPage && isSupplementMode" class="success-message">
            <i class="bi bi-check-circle-fill"></i>
            <span>您正在补充<strong>{{ selectedResource.title || selectedResource.title_en }}</strong>的资源，请直接上传新图片。</span>
          </div>
          <div v-else>
            <div class="search-box">
                <input 
                  type="text" 
                class="custom-input" 
                  placeholder="输入资源标题关键词..." 
                  v-model="searchQuery"
                  @input="searchResources"
                  :disabled="isSupplementMode"
                >
            </div>
            
            <!-- 搜索状态和结果 -->
            <div v-if="searching" class="loading-inline">
              <div class="spinner small-spinner"></div>
              <span>搜索中...</span>
            </div>
            <div v-else-if="searchResults.length > 0" class="search-results">
              <h5>找到以下相似资源:</h5>
              <div class="results-list">
                <div 
                  v-for="result in searchResults" 
                  :key="result.id"
                  class="result-item"
                  :class="{'active': selectedResource && selectedResource.id === result.id}"
                  @click="selectResource(result)"
                >
                  <div class="result-info">
                    <strong>{{ result.title || '无中文标题' }}</strong>
                    <small class="result-subtitle">{{ result.title_en || '无英文标题' }}</small>
                  </div>
                  <span class="result-type">{{ result.resource_type }}</span>
              </div>
              </div>
              <div class="results-actions">
                <button type="button" class="btn-custom btn-outline" @click="clearSearch">
                  <i class="bi bi-arrow-repeat"></i>
                  <span class="btn-text">重新搜索</span>
                </button>
                <button 
                  type="button" 
                  class="btn-custom btn-primary" 
                  :disabled="!selectedResource" 
                  @click="confirmSupplement"
                >
                  确认补充此资源
                </button>
              </div>
            </div>
            <div v-else-if="hasSearched && searchResults.length === 0" class="empty-results">
              <i class="bi bi-check-circle-fill"></i>
              <span>没有找到相似资源，您可以提交新资源!</span>
              <button type="button" class="btn-custom btn-outline small" @click="clearSearch">
                <i class="bi bi-arrow-repeat"></i>
                <span class="btn-text">重新搜索</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 表单标题 -->
      <div class="form-header">
        <h3>{{ isSupplementMode ? '补充资源信息' : '新增资源信息' }}</h3>
        <div v-if="isSupplementMode" class="mode-badge">补充模式</div>
      </div>
      
      <!-- 已选资源信息（补充模式） -->
      <div v-if="isSupplementMode" class="selected-resource-card">
        <h4>您正在补充以下资源:</h4>
        <div class="resource-info">
          <div class="info-row">
            <span class="info-label">中文标题:</span>
            <span class="info-value">{{ selectedResource.title || '无' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">英文标题:</span>
            <span class="info-value">{{ selectedResource.title_en || '无' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">类型:</span>
            <span class="info-value">{{ selectedResource.resource_type }}</span>
          </div>
        </div>
      </div>
      
      <!-- 中文名称 -->
      <div class="form-group" v-if="!isSupplementMode">
        <label for="title" class="form-label">中文名称</label>
        <input 
          type="text" 
          class="custom-input" 
          id="title" 
          v-model="form.title" 
          placeholder="输入资源的中文名称"
        >
        <div class="form-hint">中文名称或英文名称至少填写一项</div>
      </div>
      
      <!-- 英文名称 -->
      <div class="form-group" v-if="!isSupplementMode">
        <label for="title_en" class="form-label">英文名称</label>
        <input 
          type="text" 
          class="custom-input" 
          id="title_en" 
          v-model="form.title_en" 
          placeholder="输入资源的英文名称"
        >
      </div>
      
      <!-- 资源类型（优化后的多选） -->
      <div class="form-group" v-if="!isSupplementMode">
        <label for="resource_types" class="form-label">资源类型</label>
        <div class="resource-type-options">
          <div 
            v-for="(type, index) in resourceTypes" 
            :key="index" 
            class="resource-type-option"
            :class="{ 'selected': isTypeSelected(type) }"
                @click="toggleType(type)"
              >
            <span class="option-text">{{ type }}</span>
            <i v-if="isTypeSelected(type)" class="bi bi-check-circle-fill check-icon"></i>
              </div>
            </div>
        <div class="selected-types-preview">
          <span>已选类型：</span>
          <span v-if="selectedTypes.length > 0" class="selected-type-text">{{ selectedTypes.join(', ') }}</span>
          <span v-else class="text-muted">未选择</span>
          </div>
      </div>
      
      <!-- 简介 -->
      <div class="form-group" v-if="!isSupplementMode">
        <label for="description" class="form-label">简介</label>
        <textarea 
          class="custom-textarea" 
          id="description" 
          rows="4" 
          v-model="form.description" 
          placeholder="请描述资源的背景、内容、特点等信息..."
          required
        ></textarea>
      </div>
      
      <!-- 资源链接 -->
      <div class="form-group">
        <label class="form-label">
          资源链接
          <span class="optional-badge">可选</span>
        </label>
        <div class="links-card">
          <p class="link-info-text">
              您可以提供网盘链接或在线观看地址，方便其他用户获取资源。每种类型可添加多个链接。
            </p>
            
            <!-- 链接类型选项卡 -->
          <div class="links-tabs">
                <button 
              v-for="(urls, category) in resourceLinks" 
              :key="category"
              class="tab-btn" 
                  :class="{ active: activeCategory === category }"
                  @click.prevent="activeCategory = category"
                >
                  {{ getCategoryDisplayName(category) }}
              <span v-if="urls.length > 0" class="tab-badge">{{ urls.length }}</span>
                </button>
          </div>
            
            <!-- 链接输入区域 -->
          <div class="links-content">
            <div v-for="(category, categoryIndex) in Object.keys(resourceLinks)" :key="categoryIndex" 
                  v-show="activeCategory === category"
                  class="link-category-content">
              <div v-if="resourceLinks[category].length === 0" class="empty-links">
                <i class="bi bi-link-45deg empty-icon"></i>
                <p>暂无{{ getCategoryDisplayName(category) }}链接，点击下方按钮添加</p>
              </div>
              
              <!-- 已添加的链接 -->
              <div class="links-list">
                <div class="link-item" v-for="(link, index) in resourceLinks[category]" :key="index">
                  <div class="link-inputs">
                    <div class="input-group">
                      <div class="input-prefix">
                        <i class="bi bi-link-45deg"></i>
                        <span>链接</span>
                      </div>
                      <input 
                        type="text" 
                        class="custom-input" 
                        v-model="link.url" 
                        placeholder="输入链接地址"
                      >
                    </div>
                    
                    <div class="input-group">
                      <div class="input-prefix">
                        <i class="bi bi-key"></i>
                        <span>密码</span>
                      </div>
                      <input 
                        type="text" 
                        class="custom-input" 
                        v-model="link.password" 
                        placeholder="提取码(可选)"
                      >
                    </div>
                    
                    <div class="input-group">
                      <div class="input-prefix">
                        <i class="bi bi-info-circle"></i>
                        <span>备注</span>
                      </div>
                      <input 
                        type="text" 
                        class="custom-input" 
                        v-model="link.note" 
                        placeholder="如:第1季"
                      >
                    </div>
                  </div>
                  
                    <button 
                      type="button" 
                    class="remove-link-btn"
                      @click="removeLink(category, index)"
                      title="删除链接"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                </div>
              </div>
              
              <!-- 添加链接按钮 -->
              <div class="add-link-container">
                <button 
                  type="button" 
                  class="btn-custom btn-outline add-link-btn"
                  @click="addLink(category)"
                >
                  <i class="bi bi-plus-circle"></i> 添加{{ getCategoryDisplayName(category) }}链接
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图片上传 -->
      <div class="form-group">
        <label class="form-label">
          {{ isSupplementMode ? '补充资源图片' : '图片上传' }}
          <span class="image-count-badge">最多10张</span>
        </label>
        <div 
          class="dropzone-container" 
          :class="{'active-dropzone': isDragging}"
          @dragenter.prevent="isDragging = true"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
        >
          <div class="dropzone-content">
            <div v-if="uploadedImages.length < 10">
              <i class="bi bi-cloud-arrow-up-fill dropzone-icon"></i>
              <p>拖拽图片文件到此处，或</p>
              <label for="file-upload" class="btn-custom btn-outline file-upload-btn">
                <i class="bi bi-image"></i> <span class="file-btn-text">选择文件</span>
              </label>
              <input 
                type="file" 
                id="file-upload" 
                @change="handleFilesSelection" 
                multiple 
                accept="image/*" 
                class="d-none"
              >
              <p class="upload-hint">支持同时上传多个文件</p>
            </div>
            <div v-else class="upload-limit-reached">
              <i class="bi bi-exclamation-circle"></i>
              <p>已达到最大上传数量（10张）</p>
            </div>
          </div>
        </div>
        
        <!-- 上传进度 -->
        <div v-if="uploading" class="upload-progress">
          <div class="progress-info">
            <div class="spinner"></div>
            <div>正在上传图片 {{ currentUploadIndex }}/{{ totalUploadCount }}，请稍等...</div>
          </div>
          <div class="progress-bar-container">
            <div 
              class="progress-bar-inner" 
              :style="{width: `${uploadProgress}%`}" 
            >{{ uploadProgress }}%</div>
          </div>
        </div>
        
        <!-- 已上传图片预览 -->
        <div v-if="uploadedImages.length > 0" class="image-preview-section">
          <div class="preview-header">
            <h5>已上传 {{ uploadedImages.length }}/10 张图片</h5>
            <button 
              type="button" 
              class="btn-custom btn-outline btn-sm" 
              @click="clearAllImages"
              v-if="uploadedImages.length > 0"
            >
              <i class="bi bi-trash"></i> 清空所有
            </button>
          </div>
          <div class="image-grid">
            <div class="image-item" v-for="(image, index) in uploadedImages" :key="index">
              <div class="image-preview-container">
                <img :src="image" class="image-preview" alt="预览">
                <div class="image-overlay">
                <button 
                  type="button" 
                    class="image-action-btn remove-btn"
                  @click="removeImage(index)"
                >
                    <i class="bi bi-trash"></i> 删除
                </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="error" class="error-message">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ error }}
      </div>
      
      <div class="form-actions">
        <router-link to="/" class="btn-custom btn-outline">取消</router-link>
        <button 
          type="submit" 
          class="btn-custom btn-primary" 
          :disabled="submitting || (!isSupplementMode && uploadedImages.length === 0)"
        >
          <i class="bi bi-cloud-upload"></i> {{ isSupplementMode ? '提交资源补充' : '提交新资源' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { calculateFileHash, getFileExtension } from '../utils/imageUtils'

const router = useRouter()
const route = useRoute()
const submitting = ref(false)
const submitSuccess = ref(false)
const error = ref(null)
const uploading = ref(false)
const uploadedImages = ref([])
const selectedTypes = ref([])
const isDragging = ref(false)
const uploadProgress = ref(0)
const currentUploadIndex = ref(0)
const totalUploadCount = ref(0)
const showTypeDropdown = ref(false)

// 资源搜索相关
const searchQuery = ref('')
const searching = ref(false)
const searchResults = ref([])
const hasSearched = ref(false)
const selectedResource = ref(null)
const isSupplementMode = ref(false)
const isFromDetailPage = ref(false)

// 防抖定时器
let searchTimeout = null

// 资源类型选项
const resourceTypes = [
  '幽默', '讽刺', '冒险', '科幻', '动作', '奇幻', 
  '恐怖', '犯罪', '悬疑', '浪漫', '历史', '战争'
]

// 计算可选的类型（排除已选中的）
const availableTypes = computed(() => {
  return resourceTypes
})

const form = reactive({
  title: '',
  title_en: '',
  description: '',
  resource_type: '',
  images: []
})

// 计算得到的resource_type字段，将选中的类型转换为逗号分隔的字符串
const formattedResourceType = computed(() => {
  return selectedTypes.value.join(',')
})

// 搜索资源
const searchResources = () => {
  // 防抖处理
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    hasSearched.value = false
    return
  }
  
  searchTimeout = setTimeout(async () => {
    searching.value = true
    searchResults.value = []
    
    try {
      const response = await axios.get(`/api/resources/public?search=${encodeURIComponent(searchQuery.value)}`)
      searchResults.value = response.data
      hasSearched.value = true
    } catch (err) {
      console.error('搜索资源失败:', err)
      error.value = '搜索资源失败，请稍后重试'
    } finally {
      searching.value = false
    }
  }, 300)
}

// 选择已有资源进行补充
const selectResource = (resource) => {
  selectedResource.value = resource
}

// 确认补充模式
const confirmSupplement = () => {
  if (!selectedResource.value) return
  
  isSupplementMode.value = true
  // 清除搜索结果，保留选定的资源
  searchResults.value = []
  hasSearched.value = true
}

// 取消补充模式
const cancelSupplement = () => {
  isSupplementMode.value = false
  selectedResource.value = null
  isFromDetailPage.value = false
}

// 清除搜索
const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  hasSearched.value = false
  selectedResource.value = null
  isSupplementMode.value = false
  isFromDetailPage.value = false
}

// 类型选择相关方法
const toggleTypeDropdown = () => {
  showTypeDropdown.value = !showTypeDropdown.value
}

const toggleType = (type) => {
  const index = selectedTypes.value.indexOf(type)
  if (index === -1) {
    selectedTypes.value.push(type)
  } else {
    selectedTypes.value.splice(index, 1)
  }
}

const removeType = (type) => {
  const index = selectedTypes.value.indexOf(type)
  if (index !== -1) {
    selectedTypes.value.splice(index, 1)
  }
}

const isTypeSelected = (type) => {
  return selectedTypes.value.includes(type)
}

// 点击外部关闭下拉框
const handleClickOutside = (event) => {
  const container = document.querySelector('.type-select-container')
  if (container && !container.contains(event.target)) {
    showTypeDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // 检查URL参数是否包含补充资源的指示
  const supplementId = route.query.supplementId
  const supplementMode = route.query.supplementMode === 'true'
  
  // 如果有指定要补充的资源ID，自动获取该资源并进入补充模式
  if (supplementId && supplementMode) {
    fetchResourceForSupplement(supplementId)
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 处理文件拖放
const handleFileDrop = (event) => {
  isDragging.value = false
  const files = [...event.dataTransfer.files]
  if (files.length > 0) {
    uploadFiles(files)
  }
}

// 处理文件选择
const handleFilesSelection = (event) => {
  const files = [...event.target.files]
  if (files.length > 0) {
    uploadFiles(files)
  }
}

// 上传多个文件
const uploadFiles = async (files) => {
  // 过滤非图片文件
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  
  // 计算可以上传的数量
  const remainingSlots = 10 - uploadedImages.value.length
  const filesToUpload = imageFiles.slice(0, remainingSlots)
  
  if (filesToUpload.length === 0) return
  
  uploading.value = true
  error.value = null
  uploadProgress.value = 0
  currentUploadIndex.value = 0
  totalUploadCount.value = filesToUpload.length
  
  try {
    for (let i = 0; i < filesToUpload.length; i++) {
      currentUploadIndex.value = i + 1
      
      // 先计算文件的哈希值
      const file = filesToUpload[i]
      const fileHash = await calculateFileHash(file)
      
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post('/api/resources/upload-images/', formData)
      
      // 添加图片URL到已上传列表
      uploadedImages.value.push(response.data.filename)
      
      // 更新进度
      uploadProgress.value = Math.round(((i + 1) / filesToUpload.length) * 100)
    }
    
    // 清除选择的文件
    document.getElementById('file-upload').value = ''
  } catch (err) {
    console.error('上传图片失败:', err)
    error.value = '上传图片失败，请稍后重试'
  } finally {
    uploading.value = false
  }
}

// 移除单张图片
const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

// 清空所有图片
const clearAllImages = () => {
  if (confirm('确定要清空所有已上传的图片吗？')) {
    uploadedImages.value = []
  }
}

// 获取要补充的资源信息
const fetchResourceForSupplement = async (resourceId) => {
  searching.value = true
  
  try {
    // 获取资源详情
    const response = await axios.get(`/api/resources/${resourceId}`)
    const resourceData = response.data
    
    // 设置为已选资源
    selectedResource.value = resourceData
    
    // 进入补充模式，并标记是从详情页直接进入的
    isSupplementMode.value = true
    isFromDetailPage.value = true
    hasSearched.value = true
    
    // 更新页面标题，显示正在补充的资源
    searchQuery.value = resourceData.title || resourceData.title_en
  } catch (err) {
    console.error('获取资源详情失败:', err)
    error.value = '获取资源详情失败，请稍后重试'
  } finally {
    searching.value = false
  }
}

// 资源链接相关数据
const resourceLinks = reactive({
  "magnet": [],
  "ed2k": [],
  "uc": [],
  "mobile": [],
  "tianyi": [],
  "quark": [],
  "115": [],
  "aliyun": [],
  "pikpak": [],
  "baidu": [],
  "123": [],
  "online": [],
  "others": []
})

// 网盘类型显示名称映射
const categoryDisplayNames = {
  "magnet": "磁力链接",
  "ed2k": "电驴(ed2k)",
  "uc": "UC网盘",
  "mobile": "移动云盘",
  "tianyi": "天翼云盘",
  "quark": "夸克网盘",
  "115": "115网盘",
  "aliyun": "阿里云盘",
  "pikpak": "PikPak",
  "baidu": "百度网盘",
  "123": "123网盘",
  "online": "在线观看",
  "others": "其他链接"
}

// 当前激活的链接类型
const activeCategory = ref("magnet")

// 获取类型显示名称
const getCategoryDisplayName = (category) => {
  return categoryDisplayNames[category] || category
}

// 添加链接
const addLink = (category) => {
  resourceLinks[category].push({
    url: '',
    password: '',
    note: ''
  })
}

// 删除链接
const removeLink = (category, index) => {
  resourceLinks[category].splice(index, 1)
}

// 提交资源
const submitResource = async () => {
  // 非补充模式下验证必填字段
  if (!isSupplementMode.value) {
    // 验证中英文名称至少填写一个
    if (!form.title && !form.title_en) {
      error.value = '中文名称和英文名称至少填写一项'
      return
    }
    
    // 确保至少选择了一个类型
    if (selectedTypes.value.length === 0) {
      error.value = '请至少选择一个资源类型'
      return
    }
    
    // 新增资源模式下必须有图片
    if (uploadedImages.value.length === 0) {
      error.value = '请至少上传一张图片'
      return
    }
  }
  
  // 处理资源链接
  const linksToSubmit = {}
  let hasLinks = false
  
  for (const category in resourceLinks) {
    // 过滤掉空链接
    const validLinks = resourceLinks[category].filter(link => link.url.trim() !== '')
    if (validLinks.length > 0) {
      linksToSubmit[category] = validLinks
      hasLinks = true
    }
  }
  
  submitting.value = true
  error.value = null
  
  try {
    if (isSupplementMode.value) {
      // 补充资源模式 - 添加图片和/或链接到已有资源
      await axios.put(`/api/resources/${selectedResource.value.id}/supplement`, {
        images: uploadedImages.value,
        links: hasLinks ? linksToSubmit : undefined
      })
    } else {
      // 新增资源模式
      await axios.post('/api/resources/', {
        title: form.title,
        title_en: form.title_en,
        description: form.description,
        resource_type: formattedResourceType.value,
        images: uploadedImages.value,
        links: hasLinks ? linksToSubmit : undefined
      })
    }
    
    submitSuccess.value = true
  } catch (err) {
    console.error('提交资源失败:', err)
    error.value = '提交资源失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.title = ''
  form.title_en = ''
  form.description = ''
  selectedTypes.value = []
  uploadedImages.value = []
  submitSuccess.value = false
  error.value = null
  searchQuery.value = ''
  searchResults.value = []
  hasSearched.value = false
  selectedResource.value = null
  isSupplementMode.value = false
  isFromDetailPage.value = false
  
  // 清空资源链接
  for (const category in resourceLinks) {
    resourceLinks[category] = []
  }
  
  // 重置当前激活的链接类型
  activeCategory.value = "magnet"
}
</script>

<style scoped>
/* 整体布局 */
.submit-resource {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 英雄区域样式 */
.hero-section {
  text-align: center;
  padding: 4rem 0;
  margin-bottom: 3rem;
  background: rgba(255, 255, 255, 0.4);
  border-radius: var(--card-radius);
  box-shadow: 
    0 25px 45px rgba(0, 0, 0, 0.1),
    inset 0 -2px 6px rgba(255, 255, 255, 0.7),
    inset 2px 2px 6px rgba(255, 255, 255, 1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  position: relative;
  overflow: hidden;
  z-index: 1;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.hero-section:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.15),
    inset 0 -2px 6px rgba(255, 255, 255, 0.7),
    inset 2px 2px 6px rgba(255, 255, 255, 1);
}

/* 添加炫彩背景元素 */
.hero-section::before {
  content: "";
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  z-index: -1;
  background: 
    radial-gradient(circle at 30% 30%, rgba(255, 105, 180, 0.15) 0%, transparent 30%),
    radial-gradient(circle at 70% 40%, rgba(64, 224, 208, 0.15) 0%, transparent 30%),
    radial-gradient(circle at 40% 80%, rgba(255, 215, 0, 0.15) 0%, transparent 30%),
    radial-gradient(circle at 80% 70%, rgba(123, 104, 238, 0.15) 0%, transparent 30%);
  animation: rotateSlow 20s infinite linear;
}

@keyframes rotateSlow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  color: var(--primary-color);
  letter-spacing: -1px;
  position: relative;
  z-index: 2;
  text-shadow: 
    3px 3px 0 rgba(99, 102, 241, 0.2),
    6px 6px 10px rgba(0, 0, 0, 0.1);
  transform-style: preserve-3d;
  transform: perspective(500px) translateZ(10px);
}

.hero-subtitle {
  font-size: 1.35rem;
  color: var(--gray-color);
  max-width: 600px;
  margin: 0 auto;
  font-weight: 500;
  letter-spacing: -0.2px;
  position: relative;
  z-index: 2;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
}

.loader {
  width: 60px;
  height: 60px;
  border: 3px solid rgba(99, 102, 241, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
  box-shadow: 0 5px 15px rgba(99, 102, 241, 0.15);
}

.small-spinner {
  width: 20px;
  height: 20px;
  border-width: 2px;
  margin-right: 10px;
}

.loading-inline {
  display: flex;
  align-items: center;
  margin: 1rem 0;
  color: var(--gray-color);
}

/* 成功提交卡片 */
.success-card {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--card-radius);
  padding: 3rem;
  text-align: center;
  box-shadow: var(--box-shadow);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: var(--glass-border);
  animation: fadeInUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.success-icon {
  font-size: 4rem;
  color: var(--success-color);
  margin-bottom: 1.5rem;
  animation: pulse 2s infinite ease-in-out;
}

.success-card h3 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--success-color);
}

.success-card p {
  font-size: 1.1rem;
  color: var(--gray-color);
  max-width: 80%;
  margin: 0 auto 0.5rem;
}

.success-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

/* 表单卡片 */
.form-card {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--card-radius);
  padding: 2rem;
  margin-bottom: 3rem;
  box-shadow: var(--box-shadow);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: var(--glass-border);
  animation: fadeIn 0.5s ease;
}

/* 提示横幅 */
.info-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 1rem 1.5rem;
  border-radius: var(--border-radius);
  margin-bottom: 2rem;
  font-weight: 500;
}

.info-banner i {
  font-size: 1.25rem;
}

/* 搜索卡片 */
.search-card {
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--card-radius);
  overflow: hidden;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.05);
}

.card-header {
  padding: 1.25rem 1.5rem;
  background: rgba(99, 102, 241, 0.08);
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dark-color);
}

.card-body {
  padding: 1.5rem;
}

.text-note {
  color: var(--gray-color);
  margin-bottom: 1.25rem;
}

.search-box {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-btn {
  min-width: 100px;
}

.search-results {
  margin-top: 1.5rem;
}

.search-results h5 {
  margin-bottom: 1rem;
  font-weight: 600;
}

.results-list {
  margin-bottom: 1.5rem;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.result-item {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(99, 102, 241, 0.05);
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover {
  background: rgba(255, 255, 255, 0.9);
}

.result-item.active {
  background: var(--primary-gradient);
  color: white;
}

.result-info {
  display: flex;
  flex-direction: column;
}

.result-subtitle {
  font-size: 0.85rem;
  opacity: 0.8;
  margin-top: 0.25rem;
}

.result-type {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.result-item.active .result-type {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.results-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.empty-results {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
  border-radius: var(--border-radius);
  margin-top: 1rem;
  position: relative;
}

.empty-results .btn-custom {
  position: absolute;
  right: 1rem;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
}

/* 表单标题 */
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  padding-bottom: 1rem;
}

.form-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark-color);
  margin: 0;
}

.mode-badge {
  background: var(--secondary-gradient);
  color: white;
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(6, 182, 212, 0.3);
}

/* 已选资源卡片 */
.selected-resource-card {
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--card-radius);
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.selected-resource-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--dark-color);
}

.resource-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  gap: 0.5rem;
}

.info-label {
  font-weight: 600;
  min-width: 80px;
  color: var(--gray-color);
}

.info-value {
  color: var(--dark-color);
}

/* 表单组 */
.form-group {
  margin-bottom: 1.75rem;
}

.form-label {
  font-weight: 600;
  color: var(--dark-color);
  margin-bottom: 0.75rem;
  display: block;
}

.optional-badge, .image-count-badge {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--gray-color);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
  margin-left: 0.5rem;
}

.image-count-badge {
  background: rgba(6, 182, 212, 0.1);
  color: var(--secondary-color);
}

.form-hint {
  font-size: 0.85rem;
  color: var(--gray-color);
  margin-top: 0.5rem;
}

.custom-input, .custom-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: var(--border-radius);
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  color: var(--dark-color);
}

.custom-input:focus, .custom-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.custom-textarea {
  min-height: 120px;
  resize: vertical;
}

/* 资源类型多选样式 */
.resource-type-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.resource-type-option {
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(124, 58, 237, 0.1);
  border-radius: 100px;
  padding: 0.5rem 1.25rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.resource-type-option::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0));
  opacity: 0.7;
}

.resource-type-option:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(124, 58, 237, 0.15);
  border-color: rgba(124, 58, 237, 0.3);
}

.resource-type-option.selected {
  background: var(--primary-gradient);
  color: white;
  border-color: transparent;
  box-shadow: 0 5px 15px rgba(124, 58, 237, 0.25),
              inset 0 1px 2px rgba(255, 255, 255, 0.4);
}

.option-text {
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.check-icon {
  color: white;
  font-size: 0.9rem;
  position: relative;
  z-index: 1;
}

.selected-types-preview {
  font-size: 0.9rem;
  color: var(--gray-color);
  margin-top: 1rem;
}

.selected-type-text {
  font-weight: 600;
  color: var(--primary-color);
}

/* 链接管理样式 */
.links-card {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--card-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  border: var(--glass-border);
}

.link-info-text {
  font-size: 0.9rem;
  color: var(--gray-color);
  margin: 1rem;
}

.links-tabs {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 1rem 1rem 1rem 1rem;
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) rgba(255, 255, 255, 0.2);
  position: relative;
  border-bottom: 1px solid rgba(124, 58, 237, 0.1);
  flex-wrap: wrap;
}

.links-tabs::-webkit-scrollbar {
  height: 6px;
}

.links-tabs::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.links-tabs::-webkit-scrollbar-thumb {
  background: var(--primary-gradient);
  border-radius: 10px;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(124, 58, 237, 0.15);
  color: var(--dark-color);
  padding: 0.5rem 1rem;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  outline: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(124, 58, 237, 0.15);
}

.tab-btn.active {
  background: var(--primary-gradient);
  color: white;
  border-color: transparent;
  box-shadow: 0 8px 15px rgba(124, 58, 237, 0.3);
}

.tab-badge {
  background: rgba(255, 255, 255, 0.3);
  color: inherit;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 100px;
  font-weight: 700;
}

.tab-btn.active .tab-badge {
  background: rgba(255, 255, 255, 0.25);
  color: white;
}

.links-content {
  padding: 0 1rem 1rem;
}

.empty-links {
  text-align: center;
  padding: 2.5rem 0;
  color: var(--gray-color);
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.link-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--border-radius);
  padding: 1rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.link-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
}

.link-inputs {
  display: grid;
  grid-template-columns: 1fr 120px 120px;
  gap: 1rem;
  width: 100%;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.input-prefix {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: var(--gray-color);
}

.remove-link-btn {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  margin-top: 1.2rem;
}

.remove-link-btn:hover {
  background: var(--accent-color);
  color: white;
  transform: rotate(90deg);
}

.add-link-container {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
}

.add-link-btn {
  width: auto;
}

/* 拖放区域样式 */
.dropzone-container {
  border: 2px dashed rgba(99, 102, 241, 0.3);
  border-radius: var(--card-radius);
  padding: 2.5rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.active-dropzone {
  border-color: var(--primary-color);
  background-color: rgba(99, 102, 241, 0.05);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.dropzone-icon {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  opacity: 0.7;
}

.upload-hint {
  font-size: 0.9rem;
  color: var(--gray-color);
  margin-top: 1rem;
}

.upload-limit-reached {
  color: var(--accent-color);
}

.upload-limit-reached i {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

/* 上传进度 */
.upload-progress {
  margin-top: 1.25rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--border-radius);
  padding: 1rem 1.25rem;
  box-shadow: var(--box-shadow);
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
  color: var(--dark-color);
}

.progress-bar-container {
  background: rgba(124, 58, 237, 0.1);
  height: 8px;
  border-radius: 100px;
  overflow: hidden;
}

.progress-bar-inner {
  height: 100%;
  background: var(--primary-gradient);
  border-radius: 100px;
  text-indent: -9999px;
  transition: width 0.3s ease;
}

/* 图片预览区域 */
.image-preview-section {
  margin-top: 1.5rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.preview-header h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-item {
  position: relative;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.image-item:hover {
  transform: translateY(-5px);
}

.image-preview-container {
  position: relative;
  width: 100%;
  height: 150px;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  border: var(--glass-border);
  background: rgba(255, 255, 255, 0.5);
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.image-preview-container:hover .image-preview {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  opacity: 0;
  transition: opacity 0.3s ease;
  padding: 0.75rem;
}

.image-preview-container:hover .image-overlay {
  opacity: 1;
}

.image-action-btn {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.remove-btn {
  background: rgba(244, 63, 94, 0.7);
  color: white;
}

.remove-btn:hover {
  background: var(--accent-color);
  transform: translateY(-2px);
}

/* 错误消息 */
.error-message {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

/* 表单底部按钮 */
.form-actions {
  display: flex;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
  margin-top: 1rem;
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
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  box-shadow: var(--box-shadow);
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
  transform: translateY(-5px);
  box-shadow: var(--deep-shadow);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 8px 20px rgba(124, 58, 237, 0.35);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.7);
  color: var(--primary-color);
  border: 1px solid rgba(124, 58, 237, 0.2);
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.btn-custom:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-custom i {
  font-size: 1.1rem;
}

/* 动画定义 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* 响应式样式 */
@media (max-width: 992px) {
  .link-inputs {
    grid-template-columns: 1fr;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 3rem 1rem;
    margin-bottom: 2rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .form-card {
    padding: 1.5rem;
  }
  
  .results-actions {
    flex-direction: column;
  }
  
  .results-actions button {
    width: 100%;
  }
  
  .resource-type-option {
    flex: 1 1 calc(50% - 0.75rem);
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-actions .btn-custom {
    width: 100%;
  }
  
  /* 在移动端模式下隐藏按钮文本，只显示图标，但保留特定按钮的文本 */
  .btn-custom .btn-text:not(.file-btn-text) {
    display: none;
  }
  
  /* 确保文件上传按钮显示完整 */
  .file-upload-btn {
    width: auto !important;
    padding: 0.6rem 1rem !important;
    justify-content: center !important;
  }
  
  .file-upload-btn .file-btn-text {
    display: inline-block !important;
    visibility: visible !important;
    margin-left: 5px;
  }
  
  /* 对搜索相关按钮的特别处理 */
  .btn-custom.btn-outline.small {
    min-width: 40px;
    height: 40px;
    border-radius: 50%;
    padding: 0.5rem;
  }
  
  /* 图标样式优化 */
  .btn-custom i {
    font-size: 1.25rem;
    margin: 0;
  }
}

@media (max-width: 576px) {
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .resource-type-option {
    flex: 1 1 100%;
  }
}

/* 确保文件上传按钮在移动端正常显示 */
.file-upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  white-space: nowrap;
}

.file-btn-text {
  display: inline-block;
  font-size: 14px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .file-upload-btn {
    width: auto;
    padding: 8px 16px;
  }
  
  .file-btn-text {
    display: inline-block !important;
    visibility: visible !important;
  }
}
</style> 