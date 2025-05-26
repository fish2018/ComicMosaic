<template>
  <div class="admin-container">
    <div class="admin-hero">
      <h1 class="hero-title">管理控制台</h1>
      <p class="hero-subtitle">管理资源、审批内容、维护系统</p>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loader"></div>
      <p>正在加载数据，请稍候...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="bi bi-exclamation-triangle-fill"></i>
      {{ error }}
    </div>
    
    <div v-else class="admin-content">
      <!-- 修改密码卡片 -->
      <div class="admin-card">
        <div class="card-header">
          <h4><i class="bi bi-shield-lock"></i> 修改密码</h4>
          <button 
            type="button" 
            class="btn-custom btn-outline toggle-btn" 
            @click="showChangePassword = !showChangePassword"
          >
            <i :class="showChangePassword ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
            <span class="btn-text">{{ showChangePassword ? '收起' : '展开' }}</span>
          </button>
        </div>
        <div class="card-body" v-if="showChangePassword">
          <div v-if="passwordSuccess" class="success-message">
            <i class="bi bi-check-circle-fill"></i>
            密码修改成功
          </div>
          <div v-if="passwordError" class="error-message">
            <i class="bi bi-exclamation-triangle-fill"></i>
            {{ passwordError }}
          </div>
          
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label for="currentPassword" class="form-label">当前密码</label>
              <div class="input-group">
                <div class="input-prefix">
                  <i class="bi bi-key-fill"></i>
                </div>
              <input 
                type="password" 
                  class="custom-input" 
                id="currentPassword" 
                v-model="passwordForm.currentPassword" 
                required
                  placeholder="请输入当前密码"
              >
              </div>
            </div>
            
            <div class="form-group">
              <label for="newPassword" class="form-label">新密码</label>
              <div class="input-group">
                <div class="input-prefix">
                  <i class="bi bi-lock-fill"></i>
                </div>
              <input 
                type="password" 
                  class="custom-input" 
                id="newPassword" 
                v-model="passwordForm.newPassword" 
                required
                  placeholder="请输入新密码"
              >
              </div>
            </div>
            
            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认新密码</label>
              <div class="input-group">
                <div class="input-prefix">
                  <i class="bi bi-lock-fill"></i>
                </div>
              <input 
                type="password" 
                  class="custom-input" 
                id="confirmPassword" 
                v-model="passwordForm.confirmPassword" 
                required
                  placeholder="请再次输入新密码"
              >
              </div>
            </div>
            
            <div class="form-actions">
              <button 
                type="submit" 
                class="btn-custom btn-primary" 
                :disabled="passwordLoading"
              >
                <div v-if="passwordLoading" class="spinner"></div>
                <i class="bi bi-key"></i>
                <span class="btn-text">{{ passwordLoading ? '提交中...' : '修改密码' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 待审批资源卡片 -->
      <div class="admin-card">
        <div class="card-header">
          <div class="header-left">
            <h4>
              <i class="bi bi-hourglass-split"></i> 待审批资源
              <div v-if="pendingResources.length > 0" class="badge-count badge-inline">{{ pendingResources.length }}</div>
            </h4>
          </div>
        </div>
        <div class="card-body">
          <div v-if="loadingPending" class="loading-inline">
            <div class="spinner small-spinner"></div>
            <span>加载待审批资源...</span>
            </div>
          <div v-else-if="pendingResources.length === 0" class="empty-state">
            <i class="bi bi-inbox"></i>
            <p>没有待审批的资源</p>
          </div>
          <div v-else class="table-container">
            <table class="custom-table">
                <thead>
                  <tr>
                  <th>ID</th>
                  <th>标题</th>
                  <th>类型</th>
                  <th>审批类型</th>
                  <th>图片</th>
                  <th>提交时间</th>
                  <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="resource in pendingResources" :key="resource.id">
                  <td><span class="id-badge">#{{ resource.id }}</span></td>
                    <td>{{ resource.title || resource.title_en }}</td>
                  <td><span class="type-badge">{{ resource.resource_type }}</span></td>
                  <td>
                    <span 
                      class="badge-supplement" 
                      v-if="resource.has_pending_supplement || resource.supplement?.status === 'pending'"
                    >
                      补充审批
                    </span>
                    <span class="badge-initial" v-else>初始审批</span>
                  </td>
                    <td>
                      <button 
                      class="btn-custom btn-outline btn-sm view-images-btn" 
                        @click="previewImages(resource)"
                      >
                      <i class="bi bi-images"></i> {{ resource.supplement?.images?.length || resource.images?.length || 0 }}
                      </button>
                    </td>
                    <td>{{ formatDate(resource.created_at) }}</td>
                  <td class="actions-cell">
                      <router-link 
                        :to="`/admin/resource-review/${resource.id}`" 
                      class="btn-custom btn-primary btn-sm"
                      >
                      <i class="bi bi-clipboard-check"></i> 
                      <span class="btn-text">开始审核</span>
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
          </div>
        </div>
      </div>
      
      <!-- 已审批资源卡片 - 审批记录 -->
      <div class="admin-card">
        <div class="card-header">
          <h4><i class="bi bi-clipboard-check"></i> 审批记录</h4>
          <div class="header-actions">
            <button 
              type="button" 
              class="btn-custom btn-accent btn-sm" 
              @click="confirmBatchDelete"
              :disabled="selectedResources.length === 0"
            >
              <i class="bi bi-trash"></i> 
              <span class="btn-text">批量删除</span> 
              <span v-if="selectedResources.length > 0" class="badge-count">{{ selectedResources.length }}</span>
            </button>
          </div>
        </div>
        <div class="card-body">
          <div class="table-container">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>
                    <div class="checkbox-wrapper">
                      <input id="select-all" class="custom-checkbox" type="checkbox" v-model="selectAll" @change="toggleAllSelection">
                      <label for="select-all"></label>
                    </div>
                  </th>
                  <th>记录ID</th>
                  <th>资源标题</th>
                  <th>资源类型</th>
                  <th>类型</th>
                  <th>审批结果</th>
                  <th>审批时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="resource in resources" :key="resource.id">
                  <td>
                    <div class="checkbox-wrapper">
                      <input :id="`resource-${resource.id}`" class="custom-checkbox" type="checkbox" :value="resource.id" v-model="selectedResources">
                      <label :for="`resource-${resource.id}`"></label>
                    </div>
                  </td>
                  <td><span class="id-badge">#{{ resource.id }}</span></td>
                  <td>{{ resource.title || resource.title_en }}</td>
                  <td><span class="type-badge">{{ resource.resource_type }}</span></td>
                  <td>
                    <span 
                      class="badge-supplement" 
                      v-if="resource.is_supplement_approval"
                    >
                      补充审批
                    </span>
                    <span class="badge-initial" v-else>初始审批</span>
                  </td>
                  <td>
                    <span 
                      class="status-badge" 
                      :class="{
                        'status-approved': resource.status === 'approved',
                        'status-rejected': resource.status === 'rejected'
                      }"
                    >
                      {{ resource.status === 'approved' ? '已处理' : '已拒绝' }}
                    </span>
                  </td>
                  <td>{{ formatDate(resource.updated_at || resource.created_at) }}</td>
                  <td class="actions-cell">
                    <button class="btn-custom btn-outline btn-sm" @click="showApprovalDetails(resource)">
                      <i class="bi bi-info-circle"></i> 
                      <span class="btn-text">详情</span>
                    </button>
                    <button class="btn-custom btn-accent btn-sm" @click="confirmDelete(resource)">
                      <i class="bi bi-trash"></i> 
                      <span class="btn-text">删除</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- 审批详情弹窗 -->
      <div v-if="showApprovalModal" class="custom-modal" @click.self="closeApprovalDetails">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {{ selectedResource?.is_supplement_approval ? '补充内容审批详情' : '资源审批详情' }}
              </h5>
              <button type="button" class="close-btn" @click="closeApprovalDetails">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body">
              <div v-if="selectedResource">
                <!-- 基本信息卡片 -->
                <div class="detail-section">
                  <h6 class="detail-title"><i class="bi bi-info-circle"></i> 基本信息</h6>
                  <div class="detail-content">
                    <div class="detail-item">
                      <span class="detail-label">ID:</span>
                      <span class="detail-value id-badge">#{{ selectedResource.id }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">标题:</span>
                      <span class="detail-value">{{ selectedResource.title || selectedResource.title_en }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">类型:</span>
                      <span class="detail-value type-badge">{{ selectedResource.resource_type }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">审批类型:</span>
                      <span 
                        class="detail-value badge-supplement" 
                        v-if="selectedResource.is_supplement_approval"
                      >
                        补充审批
                      </span>
                      <span class="detail-value badge-initial" v-else>初始审批</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">状态:</span>
                      <span 
                        class="detail-value status-badge" 
                        :class="{
                          'status-approved': selectedResource.status === 'approved',
                          'status-rejected': selectedResource.status === 'rejected'
                        }"
                      >
                        {{ selectedResource.status === 'approved' ? '已通过' : '已拒绝' }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- 审批信息卡片 -->
                <div class="detail-section">
                  <h6 class="detail-title"><i class="bi bi-clock-history"></i> 审批信息</h6>
                  <div class="detail-content">
                    <div class="detail-item">
                      <span class="detail-label">审批时间:</span>
                      <span class="detail-value">{{ formatDate(selectedResource.updated_at || selectedResource.created_at) }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">提交时间:</span>
                      <span class="detail-value">{{ formatDate(selectedResource.created_at) }}</span>
                    </div>
                    <div class="detail-item" v-if="selectedResource.poster_image">
                      <span class="detail-label">海报:</span>
                      <span class="detail-value">{{ getImageFileName(selectedResource.poster_image) }}</span>
                    </div>
                    <div class="detail-item" v-if="selectedResource.is_supplement_approval && selectedResource.original_resource_id">
                      <span class="detail-label">原始资源:</span>
                      <router-link :to="`/resource/${selectedResource.original_resource_id}`" class="resource-link">
                        查看原始资源 (#{{ selectedResource.original_resource_id }})
                      </router-link>
                    </div>
                  </div>
                </div>
                
                <div class="detail-section">
                  <h6 class="detail-title"><i class="bi bi-chat-left-text"></i> 审批备注</h6>
                  <div class="detail-note">
                    {{ selectedResource.is_supplement_approval ? selectedResource.description : getApprovalNotes(selectedResource.description) || '无审批备注' }}
                  </div>
                </div>
                
                <div class="detail-section">
                  <h6 class="detail-title">
                    <i class="bi bi-images"></i> 已批准图片 
                    <span class="image-count">({{ selectedResource.images ? selectedResource.images.length : 0 }})</span>
                  </h6>
                  <div class="images-grid">
                    <div 
                      v-for="(image, index) in selectedResource.images" 
                      :key="index" 
                      class="image-preview-item"
                      @click="openLargeImage(image)"
                    >
                      <div class="image-card">
                        <img :src="image" :alt="`图片 ${index+1}`">
                        <div class="image-overlay">
                          <span v-if="image === selectedResource.poster_image" class="poster-badge">海报图片</span>
                        </div>
                      </div>
                    </div>
                    <div v-if="!selectedResource.images || selectedResource.images.length === 0" class="empty-images">
                      <i class="bi bi-image"></i>
                      <p>无图片</p>
                    </div>
                  </div>
                </div>
                
                <!-- 显示链接信息 -->
                <div class="detail-section" v-if="selectedResource.links && Object.keys(selectedResource.links).length > 0">
                  <h6 class="detail-title"><i class="bi bi-link-45deg"></i> 已批准链接</h6>
                  <div class="links-container">
                    <div 
                      v-for="(links, category) in selectedResource.links" 
                      :key="category" 
                      class="link-category"
                    >
                      <div class="category-name">{{ getCategoryDisplayName(category) }}</div>
                      <ul class="links-list">
                        <li v-for="(link, index) in links" :key="index" class="link-item">
                          <i class="bi bi-link-45deg"></i>
                          <span class="link-url">{{ typeof link === 'string' ? link : link.url }}</span>
                          <span v-if="typeof link === 'object' && link.password" class="link-password">
                            密码: {{ link.password }}
                          </span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div class="modal-actions">
                  <router-link 
                    v-if="!selectedResource.is_supplement_approval"
                    :to="`/resource/${selectedResource.id}`"
                    class="btn-custom btn-primary"
                    target="_blank"
                  >
                    <i class="bi bi-box-arrow-up-right"></i> 查看公开页面
                  </router-link>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-custom btn-outline" @click="closeApprovalDetails">关闭</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 删除记录确认弹窗 -->
      <div v-if="showDeleteModal" class="custom-modal" @click.self="cancelDelete">
        <div class="modal-dialog small-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title"><i class="bi bi-trash"></i> 确认删除记录</h5>
              <button type="button" class="close-btn" @click="cancelDelete">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body">
              <p class="confirm-message">确定要删除资源 <strong>{{ resourceToDelete?.title || resourceToDelete?.title_en }}</strong> 的审批记录吗？</p>
              <div class="info-box">
                <i class="bi bi-info-circle"></i>
                <div>此操作只会从管理面板中删除这条审批记录，不会影响已发布的资源本身。</div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-custom btn-outline" @click="cancelDelete">取消</button>
              <button type="button" class="btn-custom btn-accent" @click="removeResourceFromList" :disabled="deleteLoading">
                <div v-if="deleteLoading" class="spinner small-spinner"></div>
                <span>{{ deleteLoading ? '删除中...' : '确认删除' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图片预览弹窗 -->
      <div v-if="showImagePreview" class="custom-modal" @click.self="closeImagePreview">
        <div class="modal-dialog large-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title"><i class="bi bi-images"></i> 图片预览</h5>
              <button type="button" class="close-btn" @click="closeImagePreview">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body">
              <div class="preview-grid">
                <div 
                  v-for="(image, index) in previewImagesList" 
                  :key="index"
                  class="preview-item"
                  @click="openLargeImage(image)"
                >
                  <img :src="image" :alt="`预览图片 ${index+1}`">
                </div>
              </div>
              
              <!-- 大图预览 -->
              <div v-if="largeImageUrl" class="large-image-overlay" @click="closeLargeImage">
                <div class="large-image-container">
                <img :src="largeImageUrl" class="large-image" alt="大图预览">
                  <button class="close-large-img" @click.stop="closeLargeImage">
                    <i class="bi bi-x-lg"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-custom btn-outline" @click="closeImagePreview">关闭</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 批量删除确认弹窗 -->
      <div v-if="showBatchDeleteModal" class="custom-modal" @click.self="cancelBatchDelete">
        <div class="modal-dialog small-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title"><i class="bi bi-trash"></i> 确认批量删除记录</h5>
              <button type="button" class="close-btn" @click="cancelBatchDelete">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body">
              <p class="confirm-message">确定要删除选中的 <strong>{{ selectedResources.length }}</strong> 条审批记录吗？</p>
              <div class="info-box">
                <i class="bi bi-info-circle"></i>
                <div>此操作只会从管理面板中删除这些审批记录，不会影响已发布的资源本身。</div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-custom btn-outline" @click="cancelBatchDelete">取消</button>
              <button type="button" class="btn-custom btn-accent" @click="batchDeleteResources" :disabled="batchDeleteLoading">
                <div v-if="batchDeleteLoading" class="spinner small-spinner"></div>
                <span>{{ batchDeleteLoading ? '删除中...' : '确认批量删除' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { isAdmin, debugAuth } from '../utils/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const resources = ref([])
const pendingResources = ref([])
const loading = ref(true)
const loadingPending = ref(true)
const error = ref(null)
const showDeleteModal = ref(false)
const resourceToDelete = ref(null)
const deleteLoading = ref(false)
const approvalLoading = ref(null)

// 图片预览相关
const showImagePreview = ref(false)
const previewImagesList = ref([])
const largeImageUrl = ref(null) // 用于大图预览

// 密码修改相关状态
const showChangePassword = ref(false)
const passwordLoading = ref(false)
const passwordSuccess = ref(false)
const passwordError = ref(null)
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 审批详情相关
const showApprovalModal = ref(false)
const selectedResource = ref(null)

// 批量删除相关
const selectedResources = ref([])
const selectAll = ref(false)
const showBatchDeleteModal = ref(false)
const batchDeleteLoading = ref(false)

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 获取所有已审批资源
const fetchResources = async () => {
  loading.value = true
  error.value = null
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      console.log('No token found in fetchResources')
      router.push('/login')
      return
    }
    
    // 明确使用带斜杠的版本，以匹配服务器端的路由
    console.log('Fetching resources with auth token')
    const response = await axios.get('/api/resources/', {
      params: {
        include_history: true // 请求包含审批历史记录
      }
    })
    
    // 过滤出已审批的资源
    resources.value = response.data.filter(r => r.status === 'approved' || r.status === 'rejected')
    console.log(`Fetched ${resources.value.length} approved/rejected resources`)
  } catch (err) {
    console.error('获取资源失败:', err)
    if (err.response && err.response.status === 401) {
      error.value = '认证失败，请重新登录'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      error.value = '获取资源列表失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 获取待审批资源
const fetchPendingResources = async () => {
  loadingPending.value = true
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      console.log('No token found in fetchPendingResources')
      router.push('/login')
      return
    }
    
    console.log('Fetching pending resources with auth token')
    // 修复URL格式，移除尾部斜杠
    const response = await axios.get('/api/resources/pending')
    pendingResources.value = response.data
    console.log(`Fetched ${pendingResources.value.length} pending resources`)
  } catch (err) {
    console.error('获取待审批资源失败:', err)
    if (err.response && err.response.status === 401) {
      // 避免在这里显示错误，让主界面处理认证失败的情况
      console.log('Authentication failed when fetching pending resources')
      router.push('/login')
    }
  } finally {
    loadingPending.value = false
  }
}

// 审批资源
const approveResource = async (resourceId) => {
  approvalLoading.value = resourceId
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      router.push('/login')
      return
    }
    
    // 获取要审批的资源
    const resourceToApprove = pendingResources.value.find(r => r.id === resourceId);
    
    // 发送批准请求，同时将所有图片标记为已批准，并设置第一张图片为海报
    await axios.put(`/api/resources/${resourceId}/approve`, {
      status: 'approved',
      approved_images: resourceToApprove?.images || [], // 批准所有图片
      poster_image: resourceToApprove?.images?.length > 0 ? resourceToApprove.images[0] : null // 第一张图片作为海报
    })
    
    // 从待审批列表中移除
    pendingResources.value = pendingResources.value.filter(r => r.id !== resourceId)
    
    // 刷新已审批的资源列表
    await fetchResources()
  } catch (err) {
    console.error('审批资源失败:', err)
    error.value = '审批资源失败，请稍后重试'
  } finally {
    approvalLoading.value = null
  }
}

// 拒绝资源
const rejectResource = async (resourceId) => {
  approvalLoading.value = resourceId
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      router.push('/login')
      return
    }
    
    // 发送拒绝请求
    await axios.put(`/api/resources/${resourceId}/approve`, {
      status: 'rejected'
    })
    
    // 从待审批列表中移除
    pendingResources.value = pendingResources.value.filter(r => r.id !== resourceId)
    
    // 刷新已审批的资源列表
    await fetchResources()
  } catch (err) {
    console.error('拒绝资源失败:', err)
    error.value = '拒绝资源失败，请稍后重试'
  } finally {
    approvalLoading.value = null
  }
}

// 预览图片
const previewImages = (resource) => {
  previewImagesList.value = resource.supplement?.images || resource.images || [];
  showImagePreview.value = true
}

// 关闭图片预览
const closeImagePreview = () => {
  showImagePreview.value = false
  previewImagesList.value = []
  largeImageUrl.value = null // 确保关闭大图预览
}

// 打开大图预览
const openLargeImage = (imageUrl) => {
  largeImageUrl.value = imageUrl
}

// 关闭大图预览
const closeLargeImage = () => {
  largeImageUrl.value = null
}

// 修改密码
const changePassword = async () => {
  // 验证两次密码是否一致
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  
  passwordLoading.value = true
  passwordError.value = null
  passwordSuccess.value = false
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      router.push('/login')
      return
    }
    
    await axios.post('/api/auth/change-password', {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })
    
    // 清空表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
    // 显示成功消息
    passwordSuccess.value = true
    
    // 3秒后自动隐藏成功消息
    setTimeout(() => {
      passwordSuccess.value = false
    }, 3000)
    
  } catch (err) {
    console.error('修改密码失败:', err)
    if (err.response && err.response.status === 400) {
      passwordError.value = '当前密码不正确'
    } else {
      passwordError.value = '修改密码失败，请稍后重试'
    }
  } finally {
    passwordLoading.value = false
  }
}

// 确认删除
const confirmDelete = (resource) => {
  resourceToDelete.value = resource
  showDeleteModal.value = true
}

// 取消删除
const cancelDelete = () => {
  showDeleteModal.value = false
  resourceToDelete.value = null
}

// 从列表中删除记录（实际从数据库中删除记录，但不影响资源）
const removeResourceFromList = async () => {
  if (!resourceToDelete.value) return
  
  deleteLoading.value = true
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      router.push('/login')
      return
    }
    
    // 发送删除记录请求，添加参数表示只删除记录而不影响资源
    await axios.delete(`/api/resources/${resourceToDelete.value.id}/record`)
    
    // 从前端列表中移除
    resources.value = resources.value.filter(r => r.id !== resourceToDelete.value.id)
    showDeleteModal.value = false
    resourceToDelete.value = null
  } catch (err) {
    console.error('删除记录失败:', err)
    error.value = '删除记录失败，请稍后重试'
  } finally {
    deleteLoading.value = false
  }
}

// 原删除资源函数保留但不再使用
const deleteResource = async () => {
  if (!resourceToDelete.value) return
  
  deleteLoading.value = true
  
  try {
    const token = localStorage.getItem('accessToken')
    
    if (!token) {
      router.push('/login')
      return
    }
    
    await axios.delete(`/api/resources/${resourceToDelete.value.id}`)
    resources.value = resources.value.filter(r => r.id !== resourceToDelete.value.id)
    showDeleteModal.value = false
    resourceToDelete.value = null
  } catch (err) {
    console.error('删除资源失败:', err)
    error.value = '删除资源失败，请稍后重试'
  } finally {
    deleteLoading.value = false
  }
}

// 显示审批详情
const showApprovalDetails = async (resource) => {
  try {
    // 获取完整的资源数据（包括审批历史）
    // 添加is_admin_view=true参数，确保在管理页面查看时不会重定向补充审批记录
    const response = await axios.get(`/api/resources/${resource.id}?is_admin_view=true`)
    selectedResource.value = response.data
    showApprovalModal.value = true
    
    console.log('Resource details loaded with approval history:', 
                selectedResource.value.approval_history ? 
                selectedResource.value.approval_history.length : 'none')
  } catch (err) {
    console.error('获取资源详情失败:', err)
    error.value = '获取资源详情失败，请稍后重试'
  }
}

// 关闭审批详情
const closeApprovalDetails = () => {
  showApprovalModal.value = false
  selectedResource.value = null
}

// 从描述中提取审批备注
const getApprovalNotes = (description) => {
  if (!description) return null
  
  // 尝试从描述中提取审批备注
  const notesMatch = description.match(/管理员审批意见: (.+)$/s)
  return notesMatch ? notesMatch[1] : null
}

// 获取图片文件名
const getImageFileName = (imagePath) => {
  if (!imagePath) return ''
  
  try {
    const parts = imagePath.split('/')
    return parts[parts.length - 1]
  } catch (error) {
    return imagePath
  }
}

// 获取链接分类显示名称
const getCategoryDisplayName = (category) => {
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
  
  return categoryDisplayNames[category] || category
}

// 切换全选
const toggleAllSelection = () => {
  if (selectAll.value) {
    selectedResources.value = resources.value.map(r => r.id);
  } else {
    selectedResources.value = [];
  }
}

// 打开批量删除确认弹窗
const confirmBatchDelete = () => {
  if (selectedResources.value.length === 0) {
    return;
  }
  showBatchDeleteModal.value = true;
}

// 取消批量删除
const cancelBatchDelete = () => {
  showBatchDeleteModal.value = false;
}

// 批量删除资源记录
const batchDeleteResources = async () => {
  if (selectedResources.value.length === 0) {
    return;
  }
  
  batchDeleteLoading.value = true;
  
  try {
    const token = localStorage.getItem('accessToken');
    
    if (!token) {
      router.push('/login');
      return;
    }
    
    // 逐个删除选中的资源记录
    const deletePromises = selectedResources.value.map(id => 
      axios.delete(`/api/resources/${id}/record`)
    );
    
    await Promise.all(deletePromises);
    
    // 从前端列表中移除已删除的记录
    resources.value = resources.value.filter(r => !selectedResources.value.includes(r.id));
    
    // 重置选择状态
    selectedResources.value = [];
    selectAll.value = false;
    showBatchDeleteModal.value = false;
    
  } catch (err) {
    console.error('批量删除记录失败:', err);
    error.value = '批量删除记录失败，请稍后重试';
  } finally {
    batchDeleteLoading.value = false;
  }
}

onMounted(async () => {
  console.log('Admin component mounted')
  
  // 调试打印当前认证状态
  const authStatus = debugAuth()
  
  // 检查本地存储中的token和用户信息
  if (!authStatus.isAuthenticated) {
    console.error('No valid authentication found, redirecting to login')
    router.push('/login')
    return
  }
  
  if (!authStatus.isAdmin) {
    console.error('User is not an admin, redirecting to home')
    router.push('/')
    return
  }
  
  // 并行加载两个资源列表
  loading.value = true
  loadingPending.value = true
  error.value = null
  
  try {
    console.log('Starting to fetch resources and pending resources')
    const resourcesPromise = fetchResources()
    const pendingResourcesPromise = fetchPendingResources()
    
    const results = await Promise.allSettled([resourcesPromise, pendingResourcesPromise])
    
    console.log('Fetch results:', results.map(r => r.status))
    
    // 检查是否有任何请求失败
    const anyFailed = results.some(result => result.status === 'rejected')
    if (anyFailed) {
      console.warn('Some requests failed, check the error logs above')
      
      // 获取失败的原因
      const failures = results
        .filter(result => result.status === 'rejected')
        .map(result => result.reason?.response?.status || 'Unknown error')
      
      console.error('Request failures:', failures)
      
      // 如果有401错误，认证可能有问题
      if (failures.includes(401)) {
        error.value = '认证失败，请重新登录'
        setTimeout(() => {
          router.push('/login')
        }, 2000)
      } else {
        error.value = '部分数据加载失败，请刷新页面重试'
      }
    }
  } catch (e) {
    console.error('Error during Admin initialization:', e)
    error.value = '初始化失败，请稍后重试'
  } finally {
    loading.value = false
    loadingPending.value = false
  }
})
</script>

<style scoped>
/* 整体布局 */
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 英雄区域 */
.admin-hero {
  text-align: center;
  padding: 3rem 0;
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

/* 管理卡片 */
.admin-card {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--card-radius);
  box-shadow: 
    0 10px 20px rgba(0, 0, 0, 0.08),
    inset 0 -2px 6px rgba(255, 255, 255, 0.7),
    inset 2px 2px 6px rgba(255, 255, 255, 1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.admin-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 15px 30px rgba(0, 0, 0, 0.1),
    inset 0 -2px 6px rgba(255, 255, 255, 0.7),
    inset 2px 2px 6px rgba(255, 255, 255, 1);
}

/* 卡片头部 */
.card-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  background: linear-gradient(to right, rgba(99, 102, 241, 0.03), rgba(124, 58, 237, 0.08));
}

.card-header h4 {
  margin: 0;
  color: var(--dark-color);
  font-weight: 700;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-header h4 i {
  font-size: 1.2rem;
  color: var(--primary-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.badge-count {
  background: var(--accent-gradient);
  color: white;
  font-size: 0.85rem;
  padding: 0.25rem 0.5rem;
  border-radius: 100px;
  font-weight: 600;
  min-width: 24px;
  text-align: center;
}

.badge-inline {
  margin-left: 8px;
  display: inline-flex;
}

.refresh-btn, .toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

/* 卡片内容 */
.card-body {
  padding: 1.5rem;
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

/* 消息样式 */
.error-message, .success-message {
  padding: 1rem;
  border-radius: var(--border-radius);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.error-message {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
}

.success-message {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.error-message i, .success-message i {
  font-size: 1.2rem;
}

/* 加载器 */
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
  margin-right: 0;
}

.loading-inline {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  color: var(--gray-color);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--gray-color);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

/* 表格样式 */
.table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--border-radius);
  background: rgba(255, 255, 255, 0.5);
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
}

.custom-table th {
  background: rgba(99, 102, 241, 0.05);
  font-weight: 600;
  color: var(--dark-color);
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.custom-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.05);
  color: var(--gray-color);
}

.custom-table tr:last-child td {
  border-bottom: none;
}

.custom-table tr:hover td {
  background: rgba(255, 255, 255, 0.8);
}

.id-badge {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.9rem;
}

.type-badge {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
  padding: 0.2rem 0.75rem;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
}

.badge-supplement {
  background-color: #f59e0b;
  color: white;
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge-initial {
  background-color: #6366f1;
  color: white;
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.status-badge {
  padding: 0.2rem 0.75rem;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-approved {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.status-rejected {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.view-images-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

/* 自定义复选框 */
.checkbox-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-wrapper label {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  background-color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.custom-checkbox:checked + label {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.custom-checkbox:checked + label::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-wrapper:hover label {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

/* 表单操作 */
.form-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

/* 按钮样式 */
.btn-custom {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: var(--border-radius);
  border: none;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
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
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.7);
  color: var(--primary-color);
  border: 1px solid rgba(124, 58, 237, 0.2);
}

.btn-accent {
  background: var(--accent-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(244, 63, 94, 0.2);
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.btn-custom:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

/* 模态框样式 */
.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  overflow-y: auto;
  animation: fadeIn 0.3s ease;
  padding-top: 5vh;
}

.modal-dialog {
  width: 100%;
  max-width: 800px;
  animation: slideUp 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  margin: 2rem 0;
  max-height: 90vh;
  overflow-y: auto;
}

.small-dialog {
  max-width: 500px;
}

.large-dialog {
  max-width: 1000px;
}

.modal-content {
  background: rgba(255, 255, 255, 0.9);
  border-radius: var(--card-radius);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  background: linear-gradient(to right, rgba(99, 102, 241, 0.05), rgba(124, 58, 237, 0.1));
}

.modal-title {
  margin: 0;
  color: var(--dark-color);
  font-weight: 700;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-title i {
  color: var(--primary-color);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 100px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.1);
  color: var(--gray-color);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
  transform: rotate(90deg);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
  background: rgba(99, 102, 241, 0.02);
}

/* 审批详情样式 */
.detail-section {
  margin-bottom: 1.5rem;
  border-radius: var(--border-radius);
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(99, 102, 241, 0.05);
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.detail-section:hover {
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.detail-title {
  padding: 1rem;
  margin: 0;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.05);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.05);
}

.detail-title i {
  color: var(--primary-color);
}

/* 新增: 统一内容区域样式 */
.detail-content {
  padding: 1rem;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.detail-column {
  padding: 1rem;
}

.detail-item {
  display: flex;
  margin-bottom: 0.75rem;
  align-items: flex-start;
  line-height: 1.5;
}

.detail-label {
  font-weight: 600;
  color: var(--gray-color);
  min-width: 100px;
  padding-right: 1rem;
}

.detail-value {
  color: var(--dark-color);
  flex: 1;
  word-break: break-word;
}

.detail-note {
  padding: 1rem;
  color: var(--dark-color);
  white-space: pre-wrap;
  line-height: 1.6;
  background: rgba(255, 255, 255, 0.5);
}

.resource-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.resource-link:hover {
  text-decoration: underline;
}

.image-count {
  font-size: 0.9rem;
  color: var(--gray-color);
  font-weight: 400;
}

.images-grid {
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-preview-item {
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-preview-item:hover {
  transform: translateY(-5px) scale(1.02);
}

.image-card {
  position: relative;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  aspect-ratio: 1 / 1;
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.image-card:hover img {
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent);
  display: flex;
  justify-content: center;
}

.poster-badge {
  background: rgba(244, 63, 94, 0.9);
  color: white;
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
  font-weight: 600;
}

.empty-images {
  padding: 2rem;
  text-align: center;
  color: var(--gray-color);
  grid-column: 1 / -1;
}

.empty-images i {
  font-size: 2.5rem;
  opacity: 0.6;
  margin-bottom: 0.75rem;
}

/* 链接区域样式 */
.links-container {
  padding: 1rem;
}

.link-category {
  margin-bottom: 1.5rem;
}

.category-name {
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.links-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--border-radius);
  margin-bottom: 0.5rem;
}

.link-item i {
  color: var(--primary-color);
}

.link-url {
  flex: 1;
  word-break: break-all;
}

.link-password {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
  font-size: 0.85rem;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

/* 确认对话框特有样式 */
.confirm-message {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: var(--dark-color);
}

.info-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(6, 182, 212, 0.1);
  color: var(--secondary-color);
  border-radius: var(--border-radius);
}

.info-box i {
  font-size: 1.1rem;
  margin-top: 0.2rem;
}

/* 图片预览模态框特有样式 */
.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.preview-item {
  aspect-ratio: 1/1;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  cursor: zoom-in;
  transition: all 0.3s ease;
}

.preview-item:hover {
  transform: scale(1.05);
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.large-image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  cursor: zoom-out;
  animation: fadeIn 0.3s ease;
}

.large-image-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.large-image {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--border-radius);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.close-large-img {
  position: absolute;
  top: -15px;
  right: -15px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
  border: none;
  color: var(--accent-color);
  font-size: 1.2rem;
  cursor: pointer;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.close-large-img:hover {
  transform: rotate(90deg);
  background: var(--accent-color);
  color: white;
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式样式优化 */
@media (max-width: 992px) {
  .admin-container {
    padding: 1rem;
  }
  
  .admin-hero {
    padding: 1.5rem;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .admin-card {
    margin-bottom: 1.5rem;
  }
  
  .card-header {
    flex-direction: row;
    gap: 0.75rem;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
  }
  
  .header-actions {
    width: auto;
    display: flex;
    justify-content: flex-end;
  }
  
  .header-left {
    width: auto;
    justify-content: flex-start;
  }
  
  .admin-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  /* 移动端基础样式 */
  .admin-container {
    padding: 0 0.5rem;
  }
  
  .admin-hero {
    padding: 2rem 0;
    margin-bottom: 1.5rem;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .card-header {
    padding: 1rem;
    flex-wrap: nowrap; /* 强制不换行 */
    gap: 10px;
    justify-content: space-between;
  }
  
  .card-header h4 {
    font-size: 1.1rem;
    max-width: 60%; /* 限制标题宽度，给按钮留出空间 */
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .custom-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .table-container {
    margin: 0 -1rem;
    width: calc(100% + 2rem);
    overflow-x: auto;
  }
  
  .custom-table td, 
  .custom-table th {
    padding: 0.75rem 0.5rem;
  }
  
  /* 按钮布局优化 */
  .header-actions {
    margin-left: auto;
    white-space: nowrap;
  }
  
  /* 优化按钮在移动端的布局 */
  .btn-custom.btn-sm {
    padding: 0.4rem;
    font-size: 0.8rem;
    min-width: 36px;
    height: 36px;
    justify-content: center;
  }
  
  /* 改善下拉菜单在移动端的可用性 */
  .dropdown-menu {
    min-width: 200px;
  }
  
  /* 改善模态框在移动端的显示 */
  .custom-modal .modal-dialog {
    width: 95%;
    max-width: none;
  }
  
  /* 修改表单在移动端的布局 */
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  /* 修改密码按钮样式优化 */
  .form-actions {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
  }
  
  .form-actions button {
    width: auto;
    border-radius: 50%;
    min-width: 38px;
    height: 38px;
    padding: 0.5rem;
  }
  
  /* 移动端按钮仅显示图标，不显示文字 */
  .btn-text {
    display: none;
  }
  
  .btn-custom {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
    justify-content: center;
  }
  
  .btn-custom i {
    font-size: 1.1rem;
    margin-right: 0;
  }
  
  /* 确保带有徽章的按钮能正常显示 */
  .btn-custom .badge-count {
    display: inline-flex;
    position: absolute;
    top: -8px;
    right: -8px;
    min-width: 20px;
    height: 20px;
    border-radius: 50%;
    font-size: 0.75rem;
    align-items: center;
    justify-content: center;
  }
  
  /* 特殊处理某些需要文本的按钮 */
  .close-btn .btn-text,
  .confirmation-btn .btn-text {
    display: inline-block;
  }
  
  /* 批量删除按钮需要更多空间 */
  .btn-custom.btn-accent.btn-sm {
    position: relative;
    min-width: 38px;
    padding: 0.4rem;
  }
}

@media (max-width: 576px) {
  .admin-hero {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .hero-title {
    font-size: 1.4rem;
  }
  
  .hero-subtitle {
    font-size: 0.9rem;
  }
  
  .admin-card {
    margin-bottom: 1rem;
  }
  
  .card-header {
    padding: 0.75rem 1rem;
    flex-wrap: nowrap; /* 确保即使在更小的屏幕上也不换行 */
  }
  
  .card-header h4 {
    font-size: 1rem; /* 更小的字体 */
    max-width: 50%; /* 在更小的屏幕上给按钮留更多空间 */
  }
  
  .card-body {
    padding: 0.75rem;
  }
  
  /* 优化表格在小屏幕上的显示 */
  .custom-table th:nth-child(3),
  .custom-table th:nth-child(4),
  .custom-table td:nth-child(3),
  .custom-table td:nth-child(4) {
    display: none;
  }
  
  .custom-table th:first-child,
  .custom-table td:first-child {
    padding-left: 0.5rem;
  }
  
  .custom-table th:last-child,
  .custom-table td:last-child {
    padding-right: 0.5rem;
  }
  
  /* 图片预览模态框优化 */
  .modal-image-container {
    max-width: 95vw;
  }
  
  .image-close-btn {
    right: 0;
    top: -40px;
  }
  
  /* 调整按钮大小和间距 */
  .btn-custom {
    padding: 0.45rem;
    min-width: 34px;
    height: 34px;
    border-radius: 50%;
  }
  
  .btn-custom.btn-sm {
    padding: 0.35rem;
    min-width: 30px;
    height: 30px;
  }
  
  .btn-custom i {
    font-size: 1rem;
  }
  
  /* 垂直堆叠操作按钮 */
  .actions-cell {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: flex-end;
  }
  
  /* 优化弹窗提示和确认 */
  .alert {
    padding: 0.75rem;
    font-size: 0.85rem;
  }
  
  /* 模态框按钮在移动端位置调整 */
  .modal-footer {
    justify-content: space-between;
  }
  
  .modal-footer .btn-custom {
    min-width: auto;
    width: auto;
    padding: 0.45rem 0.75rem;
    border-radius: var(--border-radius);
    height: auto;
  }
  
  .modal-footer .btn-custom .btn-text {
    display: inline-block;
  }
}
</style> 