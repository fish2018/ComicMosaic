<template>
  <div class="resource-detail">
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <div v-else-if="resource" class="row">
      <!-- 编辑模式 -->
      <div v-if="isEditing" class="col-12">
        <div class="edit-form-container">
          <div class="edit-card">
            <div class="edit-card-header">
              <h3>编辑资源</h3>
              <button @click="cancelEdit" class="btn-custom btn-outline">
                <i class="bi bi-x-lg me-2"></i>取消
              </button>
            </div>
            <div class="edit-card-body">
              <form @submit.prevent="saveChanges">
                <div class="form-group">
                  <label for="title" class="form-label">中文标题</label>
                  <input type="text" class="form-control custom-input" id="title" v-model="editForm.title">
                </div>
                
                <div class="form-group">
                  <label for="titleEn" class="form-label">英文标题</label>
                  <input type="text" class="form-control custom-input" id="titleEn" v-model="editForm.title_en">
                </div>
                
                <!-- 资源类型改为多选框 -->
                <div class="form-group">
                  <label class="form-label">资源类型</label>
                  <div class="resource-type-options">
                    <div 
                      v-for="(type, index) in resourceTypeOptions" 
                      :key="index" 
                      class="resource-type-option"
                      :class="{ 'selected': isTypeSelected(type) }"
                      @click="toggleResourceType(type)"
                    >
                      <span class="option-text">{{ type }}</span>
                      <i v-if="isTypeSelected(type)" class="bi bi-check-circle-fill check-icon"></i>
                    </div>
                  </div>
                  <div class="selected-types-preview">
                    <span>已选类型：</span>
                    <span v-if="editForm.resource_type" class="selected-type-text">{{ editForm.resource_type }}</span>
                    <span v-else class="text-muted">未选择</span>
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="description" class="form-label">简介</label>
                  <textarea class="form-control custom-textarea" id="description" rows="6" v-model="editForm.description" required></textarea>
                </div>
                
                <!-- 图片管理部分的改进 -->
                <div class="form-group">
                  <label class="form-label">图片管理</label>
                  
                  <!-- 现有图片展示和管理 -->
                  <div class="image-management-section">
                    <h6 class="section-subtitle">已有图片 ({{ editForm.images.length }})</h6>
                    <div class="image-grid">
                      <div v-for="(image, index) in editForm.images" :key="index" class="image-item" :class="{'is-poster': image === editForm.poster_image}">
                        <div class="image-preview-container">
                          <img 
                            :src="getImageUrl(image)" 
                            class="image-preview" 
                            alt="资源图片" 
                            @click="previewEditImage(image)"
                          >
                          <div class="image-overlay">
                            <button 
                              type="button" 
                              class="image-action-btn set-poster-btn" 
                              @click.stop="setPosterImage(image)"
                              :disabled="image === editForm.poster_image"
                            >
                              <i class="bi bi-star-fill me-1"></i>
                              {{ image === editForm.poster_image ? '当前海报' : '设为海报' }}
                            </button>
                            <button 
                              type="button" 
                              class="image-action-btn remove-btn" 
                              @click.stop="removeImage(index)"
                              :disabled="editForm.images.length <= 1"
                            >
                              <i class="bi bi-trash me-1"></i>删除
                            </button>
                          </div>
                        </div>
                        <div class="poster-badge" v-if="image === editForm.poster_image">
                          <i class="bi bi-star-fill"></i> 海报图片
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 添加新图片 -->
                  <div class="upload-section">
                    <h6 class="section-subtitle">添加新图片</h6>
                    <div 
                      class="dropzone-container" 
                      :class="{'active-dropzone': isDragging}"
                      @dragenter.prevent="isDragging = true"
                      @dragover.prevent="isDragging = true"
                      @dragleave.prevent="isDragging = false"
                      @drop.prevent="handleFileDrop"
                    >
                      <div class="dropzone-content">
                        <i class="bi bi-cloud-arrow-up-fill dropzone-icon"></i>
                        <p>拖拽图片文件到此处，或</p>
                        <label for="file-upload" class="btn-custom btn-outline">
                          <i class="bi bi-image me-2"></i>选择文件
                        </label>
                        <input 
                          type="file" 
                          id="file-upload" 
                          @change="handleFilesSelection" 
                          multiple 
                          accept="image/*" 
                          class="d-none"
                        >
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
                  </div>
                </div>
                
                <!-- 链接管理部分 -->
                <div class="form-group">
                  <label class="form-label">资源链接管理</label>
                  <div class="links-edit-card">
                    <p class="link-info-text">
                      您可以管理网盘链接或在线观看地址，方便用户获取资源。每种类型可添加多个链接。
                    </p>
                    
                    <!-- 链接类型选项卡 -->
                    <div class="links-tabs">
                      <button 
                        v-for="(category, categoryIndex) in Object.keys(editLinks)" 
                        :key="categoryIndex"
                        class="tab-btn"
                        :class="{ active: editActiveCategory === category }"
                        @click.prevent="editActiveCategory = category"
                      >
                        {{ getCategoryDisplayName(category) }}
                        <span v-if="editLinks[category].length > 0" class="tab-badge">{{ editLinks[category].length }}</span>
                      </button>
                    </div>
                    
                    <!-- 链接输入区域 -->
                    <div class="links-content">
                      <div v-for="(category, categoryIndex) in Object.keys(editLinks)" :key="categoryIndex" 
                           v-show="editActiveCategory === category"
                           class="link-category-content">
                        <div v-if="editLinks[category].length === 0" class="empty-links">
                          <i class="bi bi-link-45deg empty-icon"></i>
                          <p>暂无{{ getCategoryDisplayName(category) }}链接，点击下方按钮添加</p>
                        </div>
                        
                        <!-- 已添加的链接 -->
                        <div class="links-list">
                          <div class="link-item" v-for="(link, index) in editLinks[category]" :key="index">
                            <div class="link-inputs">
                              <div class="input-group">
                                <div class="input-prefix">
                                  <i class="bi bi-link-45deg"></i>
                                  <span>链接</span>
                                </div>
                                <input 
                                  type="text" 
                                  class="form-control custom-input" 
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
                                  class="form-control custom-input" 
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
                                  class="form-control custom-input" 
                                  v-model="link.note" 
                                  placeholder="如:第1季"
                                >
                              </div>
                            </div>
                            
                            <button 
                              type="button" 
                              class="remove-link-btn"
                              @click="removeEditLink(category, index)"
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
                            @click="addEditLink(category)"
                          >
                            <i class="bi bi-plus-circle me-2"></i> 添加{{ getCategoryDisplayName(category) }}链接
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-if="saveError" class="save-error">
                  <i class="bi bi-exclamation-triangle-fill me-2"></i>
                  {{ saveError }}
                </div>
                
                <div class="form-actions">
                  <button type="submit" class="btn-custom btn-primary save-btn" :disabled="saving">
                    <span v-if="saving" class="spinner small-spinner me-1"></span>
                    <i v-else class="bi bi-check-circle me-2"></i>
                    保存更改
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 查看模式 -->
      <template v-else>
        <div class="resource-header">
          <div class="header-content">
            <div class="titles">
              <!-- 标题区域包装 -->
              <div class="title-wrapper">
                <!-- 中文标题 -->
                <h1 class="title">{{ resource.title }}</h1>
                <!-- 类型标签 - 移到标题右侧 -->
                <div class="resource-type-badge">
                  {{ resource.resource_type }}
                </div>
              </div>
              <!-- 英文标题 -->
              <h2 class="subtitle">{{ resource.title_en }}</h2>
            </div>
            <div class="action-buttons">
              <button 
                @click="toggleLike" 
                class="btn-custom btn-like"
                :class="{'liked': isLiked}"
              >
                <i :class="isLiked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i><span class="btn-text">{{isLiked ? '已喜欢' : '喜欢'}}</span>
                <span class="like-count" v-if="resource.likes_count > 0">{{resource.likes_count}}</span>
              </button>
              <button 
                @click="goToSupplementResource" 
                class="btn-custom btn-secondary"
                v-if="resource.status === 'approved'"
              >
                <i class="bi bi-plus-circle"></i><span class="btn-text">补充资源</span>
              </button>
              <button @click="startEdit" class="btn-custom btn-primary" v-if="isUserAdmin">
                <i class="bi bi-pencil-square"></i><span class="btn-text">编辑</span>
              </button>
              <button @click="confirmDelete" class="btn-custom btn-danger" v-if="isUserAdmin">
                <i class="bi bi-trash"></i><span class="btn-text">删除</span>
              </button>
            </div>
          </div>
        </div>

        <div class="resource-content">
          <div class="media-section">
            <!-- 大图展示区 -->
            <div class="main-image-container">
              <img 
                :src="getImageUrl(currentImage)" 
                class="resource-poster" 
                :alt="resource.title || resource.title_en"
              >
            </div>
            
            <!-- 缩略图滚动区 -->
            <div class="thumbnails-container" v-if="resource.images && resource.images.length > 1">
              <div class="thumbnails-scroll">
                <div 
                  v-for="(image, index) in resource.images" 
                  :key="index" 
                  class="thumbnail" 
                  :class="{ active: currentImage === image }"
                  @click="selectImage(image)"
                >
                  <img 
                    :src="getImageUrl(image)" 
                    class="thumbnail-img" 
                    :alt="`缩略图${index+1}`"
                  >
                </div>
              </div>
            </div>
          </div>
          
          <div class="info-section">
            <div class="description-card">
              <div class="card-header">
                <h3>简介</h3>
              </div>
              <div class="card-body">
                <p>{{ resource.description }}</p>
              </div>
            </div>
            
            <!-- 资源链接部分 -->
            <div class="links-card" v-if="hasLinks">
              <div class="card-header">
                <h3>资源链接</h3>
              </div>
              <div class="card-body">
                <div class="links-tabs">
                  <button 
                    v-for="(links, category) in resource.links" 
                    :key="category" 
                    class="tab-btn" 
                    :class="{ active: activeCategory === category }" 
                    @click.prevent="activeCategory = category"
                    v-show="links.length > 0"
                  >
                    {{ getCategoryDisplayName(category) }}
                    <span class="tab-badge">{{ links.length }}</span>
                  </button>
                </div>
                
                <div class="links-content">
                  <div v-for="(links, category) in resource.links" :key="`content-${category}`" 
                       class="tab-pane" 
                       :class="{ active: activeCategory === category }"
                       v-show="links.length > 0 && activeCategory === category">
                    
                    <div class="links-table">
                      <div class="table-header">
                        <div class="col-link">链接</div>
                        <div class="col-password">提取码</div>
                        <div class="col-note">备注</div>
                      </div>
                      <div class="table-body">
                        <div class="table-row" v-for="(link, index) in links" :key="index">
                          <div class="col-link">
                            <a 
                              :href="link.url" 
                              target="_blank" 
                              rel="noopener noreferrer"
                              class="link-url"
                            >
                              <i class="bi bi-link-45deg"></i>
                              <span class="url-text">{{ link.url }}</span>
                              <i class="bi bi-box-arrow-up-right"></i>
                            </a>
                          </div>
                          <div class="col-password">
                            <div v-if="link.password" 
                                  class="password-container" 
                                  @click="copyToClipboard(link.password)" 
                                  role="button" 
                                  tabindex="0">
                              <span ref="passwordText">{{ link.password }}</span>
                              <i class="bi bi-clipboard"></i>
                            </div>
                            <span v-else class="no-password">-</span>
                          </div>
                          <div class="col-note">
                            <span class="note-text">{{ link.note || '-' }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <div v-else class="text-center my-5">
      <p>资源不存在或已被删除</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
    
    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="custom-modal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">确认删除</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>您确定要删除 <strong>{{ resource?.title || resource?.title_en }}</strong> 吗？此操作不可恢复。</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="showDeleteModal = false">取消</button>
            <button type="button" class="btn btn-danger" @click="deleteResource" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图片预览模态框 -->
    <div v-if="previewImageUrl" class="custom-modal" @click.self="closePreviewImage">
      <div class="modal-image-container">
        <button type="button" class="btn-close image-close-btn" @click="closePreviewImage"></button>
        <img :src="getImageUrl(previewImageUrl)" class="preview-large-image" :alt="resource?.title || '图片预览'">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { isAdmin } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const resource = ref(null)
const loading = ref(true)
const error = ref(null)
const isEditing = ref(false)
const saving = ref(false)
const saveError = ref(null)
const showDeleteModal = ref(false)
const deleting = ref(false)
const currentImage = ref(null)  // 当前选中的大图

// 喜欢功能相关状态
const isLiked = ref(false)
const likeInProgress = ref(false)

const editForm = reactive({
  title: '',
  title_en: '',
  description: '',
  resource_type: '',
  poster_image: '',
  images: [] // 添加images数组存储所有图片
})

// 链接编辑相关数据
const editLinks = reactive({
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

// 编辑模式下当前激活的链接类型
const editActiveCategory = ref("magnet")

const selectedImage = ref(null)

// 计算属性检查是否为管理员
const isUserAdmin = computed(() => isAdmin())

// 处理不同状态的图片路径 (审批前的uploads路径和审批后的imgs路径)
const getImageUrl = (imagePath) => {
  if (!imagePath) return 'https://via.placeholder.com/300x400';
  return imagePath;
}

// 选择图片展示在大图区域
const selectImage = (image) => {
  currentImage.value = image;
}

// 检查本地存储中是否已喜欢该资源
const checkIfLiked = (resourceId) => {
  const likedResources = JSON.parse(localStorage.getItem('likedResources') || '{}')
  return !!likedResources[resourceId]
}

// 喜欢/取消喜欢资源
const toggleLike = async () => {
  if (likeInProgress.value) return
  
  likeInProgress.value = true
  try {
    const action = isLiked.value ? 'unlike' : 'like'
    const response = await axios.post(`/api/resources/${resource.value.id}/${action}`)
    
    // 更新资源的喜欢数量
    resource.value.likes_count = response.data.likes_count
    
    // 更新本地存储的喜欢状态
    const likedResources = JSON.parse(localStorage.getItem('likedResources') || '{}')
    if (action === 'like') {
      likedResources[resource.value.id] = true
      isLiked.value = true
    } else {
      delete likedResources[resource.value.id]
      isLiked.value = false
    }
    localStorage.setItem('likedResources', JSON.stringify(likedResources))
    
  } catch (err) {
    console.error('操作喜欢状态失败:', err)
  } finally {
    likeInProgress.value = false
  }
}

const fetchResource = async () => {
  const id = route.params.id
  if (!id) {
    router.push('/')
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`/api/resources/${id}`)
    resource.value = response.data
    
    // 检查是否已喜欢该资源
    isLiked.value = checkIfLiked(resource.value.id)
    
    // 初始化当前图片
    if (resource.value.images && resource.value.images.length > 0) {
      // 如果有海报图片，优先显示海报图片
      if (resource.value.poster_image) {
        currentImage.value = resource.value.poster_image
      } else {
        currentImage.value = resource.value.images[0]
      }
    }
  } catch (err) {
    console.error('获取资源详情失败:', err)
    error.value = '获取资源详情失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 新增变量
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const currentUploadIndex = ref(0)
const totalUploadCount = ref(0)

// 开始编辑
const startEdit = () => {
  if (!resource.value) return
  
  // 复制当前资源数据到表单
  editForm.title = resource.value.title || ''
  editForm.title_en = resource.value.title_en || ''
  editForm.description = resource.value.description || ''
  editForm.resource_type = resource.value.resource_type || ''
  editForm.poster_image = resource.value.poster_image || ''
  editForm.images = [...(resource.value.images || [])] // 复制所有图片
  
  // 初始化编辑链接
  for (const category in editLinks) {
    editLinks[category] = []
  }
  
  // 复制当前资源的链接到编辑表单
  if (resource.value.links) {
    for (const category in resource.value.links) {
      if (editLinks[category] && resource.value.links[category]) {
        // 确保链接格式一致，处理字符串和对象两种格式
        editLinks[category] = resource.value.links[category].map(link => {
          if (typeof link === 'string') {
            return { url: link, password: '', note: '' }
          } else {
            return { ...link }
          }
        })
      }
    }
  }
  
  // 设置第一个有链接的分类为激活状态
  for (const category in editLinks) {
    if (editLinks[category].length > 0) {
      editActiveCategory.value = category
      break
    }
  }
  
  isEditing.value = true
}

// 添加链接
const addEditLink = (category) => {
  editLinks[category].push({
    url: '',
    password: '',
    note: ''
  })
}

// 删除链接
const removeEditLink = (category, index) => {
  editLinks[category].splice(index, 1)
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  selectedImage.value = null
  saveError.value = null
}

// 设置海报图片
const setPosterImage = (image) => {
  editForm.poster_image = image
}

// 移除图片
const removeImage = (index) => {
  // 如果删除的是海报图片，则清空海报字段
  if (editForm.images[index] === editForm.poster_image) {
    editForm.poster_image = ''
  }
  editForm.images.splice(index, 1)
}

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
  
  if (imageFiles.length === 0) return
  
  uploading.value = true
  saveError.value = null
  uploadProgress.value = 0
  currentUploadIndex.value = 0
  totalUploadCount.value = imageFiles.length
  
  try {
    for (let i = 0; i < imageFiles.length; i++) {
      currentUploadIndex.value = i + 1
      
      const file = imageFiles[i]
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post('/api/resources/upload-images/', formData)
      
      // 添加图片URL到已上传列表
      editForm.images.push(response.data.filename)
      
      // 更新进度
      uploadProgress.value = Math.round(((i + 1) / imageFiles.length) * 100)
    }
    
    // 清除选择的文件
    document.getElementById('file-upload').value = ''
  } catch (err) {
    console.error('上传图片失败:', err)
    saveError.value = '上传图片失败，请稍后重试'
  } finally {
    uploading.value = false
  }
}

// 保存变更
const saveChanges = async () => {
  if (!resource.value) return
  
  saving.value = true
  saveError.value = null
  
  try {
    // 处理资源链接
    const linksToSubmit = {}
    let hasLinks = false
    
    for (const category in editLinks) {
      // 过滤掉空链接
      const validLinks = editLinks[category].filter(link => link.url.trim() !== '')
      if (validLinks.length > 0) {
        linksToSubmit[category] = validLinks
        hasLinks = true
      }
    }
    
    // 更新资源
    const response = await axios.put(`/api/resources/${resource.value.id}`, {
      title: editForm.title,
      title_en: editForm.title_en,
      description: editForm.description,
      resource_type: editForm.resource_type,
      poster_image: editForm.poster_image,
      images: editForm.images, // 提交所有图片
      links: hasLinks ? linksToSubmit : undefined // 提交链接数据
    })
    
    // 更新本地资源数据
    resource.value = response.data
    
    // 更新当前显示的图片
    if (resource.value.poster_image) {
      currentImage.value = resource.value.poster_image
    } else if (resource.value.images && resource.value.images.length > 0) {
      currentImage.value = resource.value.images[0]
    }
    
    // 退出编辑模式
    isEditing.value = false
  } catch (err) {
    console.error('保存资源失败:', err)
    saveError.value = '保存失败，请稍后重试'
  } finally {
    saving.value = false
  }
}

// 确认删除
const confirmDelete = () => {
  showDeleteModal.value = true
}

// 删除资源
const deleteResource = async () => {
  if (!resource.value) return
  
  deleting.value = true
  
  try {
    await axios.delete(`/api/resources/${resource.value.id}`)
    
    // 删除成功后返回首页
    router.push({
      path: '/',
      query: { deleted: 'success' }
    })
  } catch (err) {
    console.error('删除资源失败:', err)
    error.value = '删除资源失败，请稍后重试'
    showDeleteModal.value = false
  } finally {
    deleting.value = false
  }
}

// 图片预览相关
const previewImageUrl = ref(null)

// 预览编辑模式下的图片
const previewEditImage = (image) => {
  previewImageUrl.value = image
  document.body.style.overflow = 'hidden'
}

// 关闭预览图片
const closePreviewImage = () => {
  previewImageUrl.value = null
  document.body.style.overflow = 'auto'
}

// 跳转到资源补充页面
const goToSupplementResource = () => {
  if (!resource.value) return

  // 使用查询参数跳转到提交页面，带上该资源ID和预选状态
  router.push({
    path: '/submit',
    query: {
      supplementId: resource.value.id,
      supplementMode: 'true'
    }
  })
}

// 资源链接相关变量
const activeCategory = ref('magnet') // 默认显示的链接类型

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

// 获取类型显示名称
const getCategoryDisplayName = (category) => {
  return categoryDisplayNames[category] || category
}

// 检查资源是否有链接
const hasLinks = computed(() => {
  if (!resource.value || !resource.value.links) return false;
  
  // 检查是否有任何非空链接分类
  for (const category in resource.value.links) {
    if (resource.value.links[category] && resource.value.links[category].length > 0) {
      // 设置第一个有效的类别为活动类别
      if (!activeCategory.value || !resource.value.links[activeCategory.value] || 
          resource.value.links[activeCategory.value].length === 0) {
        activeCategory.value = category;
      }
      return true;
    }
  }
  
  return false;
});

// 复制到剪贴板的函数
const copyToClipboard = (text) => {
  const passwordContainer = event.currentTarget;
  const passwordText = passwordContainer.querySelector('span');
  const originalText = passwordText.textContent;
  
  // 复制文本到剪贴板（直接使用传入的text参数，不再需要选择文本）
  navigator.clipboard.writeText(text)
    .then(() => {
      // 在密码容器上添加复制成功的样式
      passwordContainer.classList.add('copied');
      
      // 直接在原位置显示"已复制"
      passwordText.textContent = '已复制';
      passwordText.style.color = 'var(--success-color)';
      passwordText.style.fontWeight = '700';
      
      // 1.5秒后恢复原来的密码文本和样式
      setTimeout(() => {
        passwordText.textContent = originalText;
        passwordText.style.color = '';
        passwordText.style.fontWeight = '';
        passwordContainer.classList.remove('copied');
      }, 1500);
    })
    .catch(err => {
      console.error('无法复制文本: ', err);
      alert('复制失败，请手动复制');
    });
};

// 资源类型选项 - 更改为适合美漫网站的选项
const resourceTypeOptions = [
  '幽默', '讽刺', '冒险', '科幻', '动作', '奇幻', 
  '恐怖', '犯罪', '悬疑', '浪漫', '历史', '战争'
];

// 检查类型是否被选中
const isTypeSelected = (type) => {
  if (!editForm.resource_type) return false;
  return editForm.resource_type.split(',').includes(type);
};

// 切换资源类型选择
const toggleResourceType = (type) => {
  let types = editForm.resource_type ? editForm.resource_type.split(',') : [];
  
  if (isTypeSelected(type)) {
    // 如果已选中，则移除
    types = types.filter(t => t !== type);
  } else {
    // 如果未选中，则添加
    types.push(type);
  }
  
  // 更新资源类型字段
  editForm.resource_type = types.join(',');
};

onMounted(() => {
  fetchResource()
})
</script>

<style scoped>
/* 整体布局 */
.resource-detail {
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 加载状态美化 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
}

.spinner-border {
  width: 4rem;
  height: 4rem;
  color: var(--primary-color);
  border-width: 0.25rem;
  filter: drop-shadow(0 0 8px rgba(124, 58, 237, 0.4));
  animation: spin 1.2s linear infinite, pulse 2s ease-in-out infinite alternate;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* 资源标题区域 */
.resource-header {
  position: relative;
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--card-radius);
  padding: 2.5rem;
  margin-bottom: 2rem;
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  box-shadow: var(--box-shadow);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.resource-header::before {
  content: "";
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  z-index: -1;
  background: 
    radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.1) 0%, transparent 40%),
    radial-gradient(circle at 70% 70%, rgba(6, 182, 212, 0.1) 0%, transparent 40%);
  animation: rotateSlow 25s infinite linear;
}

@keyframes rotateSlow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.5rem;
  position: relative;
  z-index: 1;
}

.titles {
  flex: 1;
  min-width: 280px;
}

.title-wrapper {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem; /* 增加PC模式下的间距 */
}

.title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: var(--dark-color);
  line-height: 1.2;
  letter-spacing: -0.03em;
  position: relative;
  display: inline-block;
  text-shadow: 2px 2px 0 rgba(124, 58, 237, 0.1);
  margin-right: 0; /* 重置右侧间距，由title-wrapper的gap控制 */
}

.title::after {
  content: "";
  position: absolute;
  bottom: -6px;
  left: 0;
  width: 60%;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.subtitle {
  font-size: 1.5rem;
  color: var(--gray-color);
  font-weight: 500;
  margin-top: 1.25rem;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.resource-type-badge {
  display: inline-block;
  background: var(--glass-background);
  color: var(--primary-color);
  font-weight: 700;
  padding: 0.6rem 1.5rem;
  border-radius: 100px;
  margin: 0; /* 重置所有边距，由title-wrapper的gap控制 */
  font-size: 0.95rem;
  letter-spacing: -0.01em;
  border: 1px solid rgba(124, 58, 237, 0.2);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  box-shadow: 
    0 4px 10px rgba(124, 58, 237, 0.15),
    inset 0 1px 1px rgba(255, 255, 255, 0.7);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  z-index: 1;
}

.resource-type-badge:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 15px rgba(124, 58, 237, 0.25);
}

/* 资源内容区域 */
.resource-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); /* 1:1.5的比例分配 */
  gap: 2.5rem;
  margin-top: 2.5rem;
}

.media-section {
  background: var(--glass-background);
  border-radius: var(--card-radius);
  padding: 1.5rem;
  box-shadow: var(--box-shadow);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  height: fit-content;
}

.main-image-container {
  width: 100%;
  border-radius: var(--border-radius);
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  cursor: zoom-in;
}

.resource-poster {
  width: 100%;
  display: block;
  transition: transform 0.5s ease;
}

.main-image-container:hover .resource-poster {
  transform: scale(1.04);
}

.thumbnails-container {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius);
  border: 1px solid rgba(255, 255, 255, 0.5);
  width: 100%;
  overflow-x: hidden; /* 控制外层容器溢出隐藏 */
}

.thumbnails-scroll {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) rgba(255, 255, 255, 0.5);
  -webkit-overflow-scrolling: touch; /* 增强iOS的滚动体验 */
  width: 100%;
  flex-wrap: nowrap; /* 确保不换行 */
  /* 修复Safari的滚动问题 */
  -webkit-transform: translateZ(0);
  transform: translateZ(0);
}

.thumbnails-scroll::-webkit-scrollbar {
  height: 5px;
}

.thumbnails-scroll::-webkit-scrollbar-thumb {
  background-color: var(--primary-color);
  border-radius: 100px;
}

.thumbnails-scroll::-webkit-scrollbar-track {
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 100px;
}

.thumbnail {
  flex: 0 0 80px;
  height: 80px;
  border-radius: var(--border-radius);
  overflow: hidden;
  cursor: pointer;
  position: relative;
  opacity: 0.7;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
}

.thumbnail:hover {
  opacity: 1;
  transform: translateY(-4px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.12);
}

.thumbnail.active {
  opacity: 1;
  transform: translateY(-6px) scale(1.05);
  box-shadow: 0 10px 20px rgba(124, 58, 237, 0.25);
  border: 2px solid var(--primary-color);
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 信息区部分 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.description-card,
.links-card {
  background: var(--glass-background);
  border-radius: var(--card-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.description-card:hover,
.links-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--deep-shadow);
}

.card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(124, 58, 237, 0.1);
  position: relative;
  overflow: hidden;
}

.card-header::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(124, 58, 237, 0.07), transparent);
  opacity: 0.8;
}

.card-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--dark-color);
  position: relative;
  display: flex;
  align-items: center;
}

.card-header h3::before {
  content: "";
  display: inline-block;
  width: 12px;
  height: 12px;
  background: var(--primary-gradient);
  margin-right: 0.75rem;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.card-body {
  padding: 1.5rem;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--dark-color);
}

.description-card .card-body {
  max-height: 400px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) rgba(255, 255, 255, 0.2);
}

.description-card .card-body::-webkit-scrollbar {
  width: 6px;
}

.description-card .card-body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.description-card .card-body::-webkit-scrollbar-thumb {
  background: var(--primary-gradient);
  border-radius: 10px;
}

/* 链接标签页 */
.links-tabs {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 1rem 1rem 1rem 1rem; /* 增加左右内边距 */
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) rgba(255, 255, 255, 0.2);
  position: relative;
  border-bottom: 1px solid rgba(124, 58, 237, 0.1);
  flex-wrap: wrap; /* 允许标签自动换行 */
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

/* 链接表格 */
.links-table {
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(124, 58, 237, 0.1);
  background: rgba(255, 255, 255, 0.6);
}

.table-header {
  display: grid;
  grid-template-columns: 5fr 2fr 3fr;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(124, 58, 237, 0.08);
  font-weight: 700;
  color: var(--dark-color);
  border-bottom: 1px solid rgba(124, 58, 237, 0.1);
}

.table-body {
  max-height: 300px;
  overflow-y: auto;
  scrollbar-width: thin;
}

.table-row {
  display: grid;
  grid-template-columns: 5fr 2fr 3fr;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(124, 58, 237, 0.05);
  transition: background-color 0.2s ease;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background-color: rgba(124, 58, 237, 0.03);
}

.col-link, .col-password, .col-note {
  display: flex;
  align-items: center;
}

.col-link {
  overflow: hidden;
}

.link-url {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: 100%;
}

.link-url:hover {
  color: var(--secondary-color);
  transform: translateY(-2px);
}

.url-text {
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

/* 修改密码容器的样式 */
.password-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(124, 58, 237, 0.08);
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none; /* 更改为 none 防止文本被选中 */
  position: relative;
}

.password-container:hover {
  background: rgba(124, 58, 237, 0.15);
  transform: translateY(-2px);
}

.password-container i {
  color: var(--primary-color);
}

.password-container.copied {
  background: rgba(124, 58, 237, 0.08);
  border: none;
  animation: subtle-pulse 1s ease;
}

/* 移除文本选择时的背景色 */
.password-container::selection,
.password-container *::selection {
  background: transparent;
}

.password-container::-moz-selection,
.password-container *::-moz-selection {
  background: transparent;
}

.note-text {
  font-style: italic;
  color: var(--gray-color);
}

/* 自定义模态框 */
.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-dialog {
  width: 100%;
  max-width: 500px;
  margin: auto;
}

.modal-content {
  background: var(--glass-background);
  border-radius: var(--card-radius);
  border: var(--glass-border);
  box-shadow: var(--deep-shadow);
  overflow: hidden;
  animation: zoomIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes zoomIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(124, 58, 237, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-weight: 700;
  color: var(--dark-color);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--gray-color);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  transition: all 0.3s ease;
  border-radius: 50%;
}

.btn-close:hover {
  color: var(--dark-color);
  background: rgba(124, 58, 237, 0.1);
  transform: rotate(90deg);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(124, 58, 237, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* 图片预览模态框 */
.modal-image-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  animation: zoomIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.preview-large-image {
  max-width: 100%;
  max-height: 90vh;
  border-radius: var(--card-radius);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  border: 3px solid rgba(255, 255, 255, 0.8);
}

.image-close-btn {
  position: absolute;
  top: -15px;
  right: -15px;
  background: white;
  color: var(--dark-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  z-index: 10;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.image-close-btn:hover {
  opacity: 1;
  transform: rotate(90deg);
}

/* 响应式样式 */
@media (max-width: 992px) {
  .resource-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  /* 恢复标题区域的原始样式 */
  .resource-header .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .titles {
    flex: 1 1 100%;
  }

  .action-buttons {
    justify-content: flex-start;
    margin-top: 1rem;
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1.25rem;
  }

  .link-inputs {
    grid-template-columns: 1fr;
  }
  
  /* 确保媒体区域在移动端不会太高 */
  .media-section {
    max-height: none;
    display: flex;
    flex-direction: column;
  }
  
  /* 确保主图像不会太大 */
  .main-image-container {
    max-height: 500px;
    display: flex;
    justify-content: center;
  }
  
  .resource-poster {
    object-fit: contain;
    max-height: 100%;
    width: auto;
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .resource-header {
    padding: 1.5rem;
  }

  /* 调整标题和类型标签在同一行显示 */
  .title-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.75rem; /* 移动端使用较小的间距 */
  }
  
  .title {
    font-size: 1.8rem;
    -webkit-line-clamp: 3;
    margin-right: 0.5rem;
  }
  
  /* 修改类型标签的样式和位置 */
  .resource-type-badge {
    margin: 0; /* 保持一致的边距策略 */
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    display: inline-flex;
    flex-shrink: 0;
  }
  
  .subtitle {
    font-size: 1.1rem;
    margin-top: 0.75rem;
    -webkit-line-clamp: 2;
  }
  
  /* 改善图片缩略图显示 */
  .thumbnails-container {
    padding: 0.5rem;
    margin-top: 1rem;
    overflow-x: hidden;
  }
  
  .thumbnails-scroll {
    gap: 0.5rem;
    padding-bottom: 0.25rem;
    overflow-x: auto !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
  }
  
  .thumbnail {
    flex: 0 0 60px;
    height: 60px;
    min-width: 60px;
  }
  
  /* 处理图片多时的布局问题 */
  .resource-content {
    display: flex;
    flex-direction: column;
  }
  
  .media-section {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
  }
  
  .info-section {
    width: 100%;
  }
  
  /* 调整卡片显示 */
  .card-header {
    padding: 1rem;
  }
  
  .card-header h3 {
    font-size: 1.25rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .description-card .card-body {
    max-height: none;
  }
  
  /* 链接表格完全重组为垂直布局 */
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
  
  .table-header {
    display: none; /* 隐藏表头 */
  }
  
  .table-body {
    max-height: none;
  }
  
  .col-link, .col-password, .col-note {
    width: 100%;
    padding: 0.5rem 0;
    display: flex;
    align-items: center;
  }
  
  .col-password, .col-note {
    padding-left: 0.25rem;
    border-top: 1px dashed rgba(124, 58, 237, 0.05);
  }
  
  /* 添加移动端标签指示文本 */
  .col-password::before {
    content: "提取码: ";
    font-weight: 600;
    color: var(--gray-color);
    margin-right: 0.5rem;
    min-width: 60px;
  }
  
  .col-note::before {
    content: "备注: ";
    font-weight: 600;
    color: var(--gray-color);
    margin-right: 0.5rem;
    min-width: 60px;
  }
  
  /* 调整链接URL显示 */
  .link-url {
    flex-wrap: wrap;
  }
  
  .url-text {
    width: 100%;
    margin: 0.25rem 0;
    white-space: normal;
    word-break: break-all;
    line-height: 1.4;
  }
  
  /* 链接选项卡 */
  .links-tabs {
    padding: 0.75rem;
    justify-content: flex-start;
    overflow-x: auto;
  }
  
  .tab-btn {
    padding: 0.4rem 0.75rem;
    font-size: 0.85rem;
    flex-shrink: 0;
  }
  
  /* 优化密码容器 */
  .password-container {
    max-width: 100%;
    overflow: hidden;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .image-preview-container {
    height: 120px;
  }
  
  /* 标题区域的移动端样式 */
  .resource-header .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  /* 按钮文本在移动端隐藏 */
  .btn-text {
    display: none;
  }
  
  /* 调整按钮样式，使图标居中 */
  .btn-custom {
    padding: 0.6rem;
    min-width: 40px;
    height: 40px;
    justify-content: center;
  }
  
  /* 优化描述区域 */
  .description-section {
    padding: 1rem;
    margin-bottom: 1.5rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .description-section h3 {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
  }
  
  .description-content {
    font-size: 0.95rem;
    line-height: 1.5;
    overflow-wrap: break-word;
    word-break: break-word;
  }
  
  /* 优化资源链接区域 */
  .resource-links-section {
    padding: 1rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .resource-links-section h3 {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
  }
  
  .link-item {
    margin-bottom: 0.75rem;
    padding: 0.75rem;
  }
  
  .link-item .link-title {
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
  }
  
  .link-item .link-url {
    font-size: 0.9rem;
    word-break: break-all;
  }
  
  /* 滚动条样式优化 */
  .thumbnails-scroll::-webkit-scrollbar {
    height: 6px;
  }
  
  .thumbnails-scroll::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 3px;
  }
  
  .thumbnails-scroll::-webkit-scrollbar-track {
    background-color: rgba(229, 231, 235, 0.3);
    border-radius: 3px;
  }
  
  .thumbnails-scroll::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.7);
  }
  
  /* 确保缩略图大小一致 */
  .thumbnail {
    min-width: 60px;
    min-height: 60px;
    width: 60px;
    height: 60px;
    flex: 0 0 auto;
    border-radius: 4px;
  }
}

@media (max-width: 576px) {
  .resource-header {
    padding: 1.25rem;
  }
  
  .title-wrapper {
    align-items: flex-start;
    gap: 0.5rem; /* 在更小屏幕上进一步减小间距 */
  }

  .title {
    font-size: 1.5rem;
    line-height: 1.3;
    max-width: calc(100% - 85px);
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .title::after {
    width: 60px;
  }
  
  /* 移动类型标签位置的样式已不需要，因为已经调整到标题右侧 */
  .resource-type-badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.7rem;
    margin-top: 0.25rem;
  }
  
  /* 进一步优化图片显示 */
  .media-section {
    padding: 0.75rem;
    margin-bottom: 1rem;
  }
  
  .main-image-container {
    max-height: 380px;
    border-radius: 8px;
  }
  
  /* 缩小缩略图 */
  .thumbnail {
    flex: 0 0 50px;
    height: 50px;
    min-width: 50px;
  }
  
  /* 优化链接项占用空间 */
  .table-row {
    padding: 0.75rem;
    margin-bottom: 0.75rem;
  }
  
  .col-link, .col-password, .col-note {
    padding: 0.35rem 0;
  }
  
  /* 调整简介卡片 */
  .description-card, .links-card {
    margin-bottom: 1.5rem;
  }
  
  /* 缩小卡片头部大小 */
  .card-header {
    padding: 0.75rem;
  }
  
  .card-header h3 {
    font-size: 1.1rem;
  }
  
  .card-body {
    padding: 0.75rem;
  }
  
  /* 确保内容完整显示 */
  .resource-detail {
    padding: 0 0.5rem;
  }

  /* 优化链接选项卡 */
  .links-tabs {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
  }
  
  .tab-btn {
    font-size: 0.85rem;
    padding: 0.5rem 0.75rem;
  }
  
  .thumbnails-container {
    margin-bottom: 1rem;
  }
  
  /* 小屏幕上完全重置缩略图容器 */
  .thumbnails-scroll {
    padding: 0.25rem 0;
    margin: 0;
    min-height: 80px;
  }
}

/* 按钮相关样式 */
@media (max-width: 768px) {
  /* 在移动端设置操作按钮样式 */
  .action-buttons {
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 1rem;
  }
  
  /* 移动端只显示图标 */
  .btn-custom {
    padding: 0.5rem;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }
  
  /* 隐藏文本 */
  .btn-custom .btn-text {
    display: none;
  }
  
  /* 调整图标大小和边距 */
  .action-buttons .btn-custom i {
    font-size: 1.25rem;
    margin: 0;
  }
}

/* 优化操作按钮 - 给按钮实际样式 */
.btn-custom {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform-origin: center;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.btn-custom:active {
  transform: scale(0.95);
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

@media (max-width: 768px) {
  .btn-custom {
    padding: 0.5rem;
    width: 42px;
    height: 42px;
    border-radius: 50%;
  }
  
  .btn-text {
    display: none;
  }
  
  .action-buttons {
    justify-content: space-around;
  }
  
  .action-buttons .btn-custom i {
    font-size: 1.25rem;
    margin: 0;
  }
}

/* 编辑表单样式 */
.edit-form-container {
  margin-bottom: 3rem;
}

.edit-card {
  background: var(--glass-background);
  border-radius: var(--card-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: fadeInUpScale 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.edit-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--deep-shadow);
}

.edit-card-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(124, 58, 237, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.edit-card-header::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(124, 58, 237, 0.07), transparent);
  opacity: 0.8;
}

.edit-card-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark-color);
  position: relative;
  display: flex;
  align-items: center;
}

.edit-card-header h3::before {
  content: "";
  display: inline-block;
  width: 12px;
  height: 12px;
  background: var(--primary-gradient);
  margin-right: 0.75rem;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.edit-card-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.75rem;
}

.form-label {
  font-weight: 600;
  color: var(--dark-color);
  margin-bottom: 0.5rem;
  display: block;
}

.custom-input, .custom-textarea {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(124, 58, 237, 0.15);
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  color: var(--dark-color);
  transition: all 0.3s ease;
  width: 100%;
  font-size: 1rem;
}

.custom-input:focus, .custom-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
  background: rgba(255, 255, 255, 0.85);
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
  margin-top: 0.5rem;
}

.selected-type-text {
  font-weight: 600;
  color: var(--primary-color);
}

/* 图片管理样式 */
.section-subtitle {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--dark-color);
  display: flex;
  align-items: center;
}

.section-subtitle::before {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  background: var(--primary-gradient);
  margin-right: 0.5rem;
  border-radius: 50%;
}

.image-management-section {
  margin-bottom: 1.5rem;
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

.image-item.is-poster {
  box-shadow: 0 10px 20px rgba(124, 58, 237, 0.2);
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

.set-poster-btn {
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
}

.set-poster-btn:hover {
  background: white;
  transform: translateY(-2px);
}

.set-poster-btn:disabled {
  background: rgba(124, 58, 237, 0.2);
  color: white;
  cursor: default;
  transform: none;
}

.remove-btn {
  background: rgba(244, 63, 94, 0.7);
  color: white;
}

.remove-btn:hover {
  background: var(--accent-color);
  transform: translateY(-2px);
}

.remove-btn:disabled {
  background: rgba(244, 63, 94, 0.4);
  cursor: default;
  transform: none;
}

.poster-badge {
  position: absolute;
  top: -10px;
  right: 10px;
  background: var(--primary-gradient);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);
  display: flex;
  align-items: center;
  gap: 0.3rem;
  z-index: 10;
}

/* 上传区域样式 */
.upload-section {
  margin-top: 2rem;
}

.dropzone-container {
  background: rgba(255, 255, 255, 0.5);
  border: 2px dashed rgba(124, 58, 237, 0.3);
  border-radius: var(--card-radius);
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.dropzone-container.active-dropzone {
  background: rgba(124, 58, 237, 0.08);
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
}

.dropzone-icon {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  display: block;
  opacity: 0.8;
}

.dropzone-content p {
  margin-bottom: 1.25rem;
  color: var(--gray-color);
}

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

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(124, 58, 237, 0.1);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.small-spinner {
  width: 16px;
  height: 16px;
  border-width: 2px;
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

/* 链接管理样式 */
.links-edit-card {
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

/* 保存错误样式 */
.save-error {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  font-weight: 500;
}

/* 表单操作区域 */
.form-actions {
  display: flex;
  justify-content: center;
  padding-top: 1.5rem;
}

.save-btn {
  min-width: 200px;
}

/* 响应式样式 */
@media (max-width: 992px) {
  .link-inputs {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .image-preview-container {
    height: 120px;
  }
}

/* 添加按钮样式 */
.btn-custom {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.25rem;
  border-radius: var(--border-radius);
  border: none;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  box-shadow: var(--box-shadow);
  white-space: nowrap;
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
  box-shadow: var(--deep-shadow);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.btn-secondary {
  background: var(--secondary-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
}

.btn-danger {
  background: var(--accent-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(244, 63, 94, 0.3);
}

/* 类型标签容器 */
.resource-types-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.resource-type-badge {
  position: relative;
  display: inline-block;
  background: var(--primary-gradient);
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.35rem 1rem;
  border-radius: 100px;
  box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);
  z-index: 2;
  transition: all 0.3s ease;
}

.resource-type-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(124, 58, 237, 0.4);
}

/* 按钮文本样式 */
.btn-text {
  margin-left: 0.5rem;
}

/* 喜欢按钮样式 */
.btn-like {
  background: rgba(255, 255, 255, 0.85);
  color: var(--dark-color);
  border: 1px solid rgba(244, 63, 94, 0.2);
  position: relative;
  overflow: visible;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.btn-like:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(244, 63, 94, 0.4);
  transform: translateY(-3px);
}

.btn-like i {
  color: var(--accent-color);
  transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.btn-like:hover i {
  transform: scale(1.2);
}

.btn-like.liked {
  background: rgba(244, 63, 94, 0.1);
  border-color: rgba(244, 63, 94, 0.3);
}

.btn-like.liked i {
  color: var(--accent-color);
}

.like-count {
  background: rgba(244, 63, 94, 0.2);
  color: var(--accent-color);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.1rem 0.5rem;
  border-radius: 100px;
  margin-left: 0.5rem;
  min-width: 22px;
  text-align: center;
}

/* 移动端喜欢按钮样式 */
@media (max-width: 768px) {
  .btn-like {
    padding: 0.5rem;
    width: 42px;
    height: 42px;
    border-radius: 50%;
  }
  
  .like-count {
    position: absolute;
    top: -5px;
    right: -5px;
    margin-left: 0;
    padding: 0.1rem 0.4rem;
    font-size: 0.7rem;
    background: var(--accent-color);
    color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  }
}

/* 针对移动端的响应式布局 */
@media (max-width: 900px) {
  .resource-content {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-top: 1.5rem;
  }
  
  .media-section {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    margin-bottom: 1rem;
  }
  
  .info-section {
    width: 100%;
  }
  
  /* 处理图片预览区域 */
  .main-image-container {
    max-height: 350px;
  }
  
  /* 确保图片缩略图可以横向滑动 */
  .thumbnails-container {
    padding: 0.5rem;
    margin-top: 1rem;
    overflow-x: hidden;
    background: rgba(255, 255, 255, 0.2);
  }
  
  .thumbnails-scroll {
    gap: 0.5rem;
    padding-bottom: 0.25rem;
    overflow-x: auto !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
  }
}

/* 针对更小屏幕设备的样式优化 */
@media (max-width: 576px) {
  .resource-content {
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .main-image-container {
    max-height: 300px;
  }
  
  .thumbnails-container {
    padding: 0.3rem;
  }
  
  .thumbnail {
    min-width: 50px;
    min-height: 50px;
    width: 50px;
    height: 50px;
  }
  
  .resource-info h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }
  
  .info-section .meta-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .description-section, 
  .resource-links-section {
    padding: 0.75rem;
    margin-bottom: 1rem;
  }
  
  .description-section h3,
  .resource-links-section h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
  
  .link-item {
    padding: 0.5rem;
    margin-bottom: 0.5rem;
  }
}
</style> 