<template>
  <div class="review-container">
    <div class="review-hero">
      <h1 class="hero-title">资源审核详情</h1>
      <p class="hero-subtitle">审核用户提交的资源内容</p>
      <div v-if="isResourceReviewed" class="status-badge status-approved">
        <i class="bi bi-check-circle-fill"></i> 
        <span v-if="isSupplementResource">该补充内容已完成审核</span>
        <span v-else>该资源已完成审核</span>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loader"></div>
      <p>正在加载资源信息...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="bi bi-exclamation-triangle-fill"></i>
      {{ error }}
    </div>
    
    <div v-else class="review-content">
      <div class="action-bar top-action-bar">
        <div></div> <!-- 使用空div保持flex布局的对齐 -->
        <router-link to="/admin" class="btn-custom btn-outline return-btn">
          <i class="bi bi-arrow-left"></i> <span class="btn-text">返回管理面板</span>
        </router-link>
      </div>
      
      <!-- 基本信息卡片 - 只读展示 -->
      <div class="review-card">
        <div class="card-header">
          <h4><i class="bi bi-info-circle"></i> 基本信息</h4>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">资源ID</span>
              <span class="info-value id-badge">#{{ resource.id }}</span>
              </div>
              
            <div class="info-item">
              <span class="info-label">提交时间</span>
              <span class="info-value">{{ formatDate(resource.created_at) }}</span>
              </div>
              
            <div class="info-item">
              <span class="info-label">原标题</span>
              <span class="info-value">{{ resource.title || '无' }}</span>
              </div>
              
            <div class="info-item">
              <span class="info-label">英文标题</span>
              <span class="info-value">{{ resource.title_en || '无' }}</span>
              </div>
              
            <div class="info-item">
              <span class="info-label">资源类型</span>
              <span class="info-value type-badge">{{ resource.resource_type || '无' }}</span>
              </div>
              
            <div class="info-item full-width">
              <span class="info-label">描述</span>
                <div class="description-box">{{ resource.description || '无' }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图片审核部分 -->
      <div class="review-card">
        <div class="card-header">
          <div class="header-left">
            <h4><i class="bi bi-images"></i> {{ isSupplementResource ? '补充图片审核' : '图片审核' }}</h4>
          </div>
          <div class="actions-group" v-if="!isResourceReviewed">
            <button class="btn-custom btn-outline" @click="selectAllImages" v-if="!isSupplementResource">
              <i class="bi bi-check-all"></i> <span class="btn-text">全选</span>
            </button>
            <button class="btn-custom btn-outline" @click="selectAllSupplementImages" v-if="isSupplementResource && supplementContent.images.length > 0">
              <i class="bi bi-check-all"></i> <span class="btn-text">全选补充图片</span>
            </button>
            <button class="btn-custom btn-outline" @click="deselectAllImages">
              <i class="bi bi-square"></i> <span class="btn-text">取消全选</span>
            </button>
            <button 
              class="btn-custom link-group-approval-btn" 
              :disabled="selectedImages.length === 0"
              @click="approveSelectedImages"
            >
              <i class="bi bi-check-lg"></i> <span class="btn-text">批准选中图片</span>
            </button>
          </div>
        </div>
        <div class="card-body">
          <!-- 已有资源的图片 (仅在补充资源时显示) -->
          <div v-if="isSupplementResource && resource.images && resource.images.length > 0" class="existing-images">
            <h5 class="section-title">已有资源图片 <span class="badge-count">({{ resource.images.length }})</span></h5>
            <div class="images-grid">
              <div v-for="(image, index) in resource.images" :key="'existing-'+index" class="image-item">
                <div class="image-card" @click="openImageViewer(image)">
                  <img :src="image" alt="已有资源图片" />
                  <div class="image-overlay">
                    <span class="badge-info">已有图片</span>
                    <span v-if="image === resource.poster_image" class="badge-warning">当前海报</span>
                  </div>
                </div>
              </div>
            </div>
            
            <h5 class="section-title mt-4">补充图片 <span class="badge-count">({{ supplementContent.images ? supplementContent.images.length : 0 }})</span></h5>
          </div>
          
          <!-- 需要审核的图片 -->
          <div class="images-grid" v-if="getImagesToAudit().length > 0">
            <div v-for="(image, index) in getImagesToAudit()" :key="'audit-'+index" class="image-item">
              <div class="image-card" 
                :class="{
                  'approved-image': approvedImages && approvedImages.includes && approvedImages.includes(image) && image !== posterImage,
                  'rejected-image': rejectedImages && rejectedImages.includes && rejectedImages.includes(image),
                  'selected-image': selectedImages && selectedImages.includes && selectedImages.includes(image) && 
                  !(approvedImages && approvedImages.includes && approvedImages.includes(image)) && 
                  !(rejectedImages && rejectedImages.includes && rejectedImages.includes(image)),
                  'poster-image': image === posterImage
                }"
              >
                <img :src="image" alt="资源图片" @click="openImageViewer(image)" />
                
                <div class="image-actions" v-if="!isResourceReviewed">
                    <button 
                    class="image-btn select-btn"
                      @click.stop="toggleImageSelection(image)"
                    :class="{'is-selected': selectedImages && selectedImages.includes && selectedImages.includes(image)}"
                    >
                      <i class="bi" :class="selectedImages && selectedImages.includes && selectedImages.includes(image) ? 'bi-check-square-fill' : 'bi-square'"></i>
                    </button>
                  
                      <button
                        v-if="canSelectAsPoster(image)" 
                    class="image-btn poster-btn"
                        @click.stop="setPosterImage(image)"
                    title="设为海报"
                      >
                    <i class="bi bi-star"></i>
                      </button>
                  
                      <button
                        v-if="image === posterImage" 
                    class="image-btn poster-btn active"
                        @click.stop="clearPosterImage()"
                    title="取消海报设置"
                      >
                    <i class="bi bi-star-fill"></i>
                      </button>
                    </div>
                
                <div class="image-status">
                  <span v-if="approvedImages && approvedImages.includes && approvedImages.includes(image)" class="status-badge status-approved">已批准</span>
                  <span v-else-if="rejectedImages && rejectedImages.includes && rejectedImages.includes(image)" class="status-badge status-rejected">已拒绝</span>
                  <span v-else-if="image === posterImage" class="status-badge status-warning">海报图片</span>
                  </div>
                  
                <div class="image-review-actions" v-if="!isResourceReviewed">
                    <button 
                    class="btn-custom btn-sm image-approval-btn" 
                      @click.stop="approveImage(image)"
                      :disabled="(approvedImages && approvedImages.includes && approvedImages.includes(image)) || 
                              (rejectedImages && rejectedImages.includes && rejectedImages.includes(image))"
                    >
                    <i class="bi bi-check-lg"></i>
                    </button>
                    <button 
                    class="btn-custom btn-sm btn-accent" 
                      @click.stop="rejectImage(image)"
                      :disabled="(approvedImages && approvedImages.includes && approvedImages.includes(image)) || 
                              (rejectedImages && rejectedImages.includes && rejectedImages.includes(image))"
                    >
                    <i class="bi bi-x-lg"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          
          <div v-else class="empty-state">
            <i class="bi bi-images"></i>
            <p>没有图片需要审核</p>
          </div>
        </div>
      </div>
      
      <!-- 链接审核部分 -->
      <div class="review-card" v-if="resource.links || (isSupplementResource && Object.keys(getSupplementLinks()).length > 0)">
        <div class="card-header">
          <div class="header-left">
            <h4><i class="bi bi-link-45deg"></i> {{ isSupplementResource ? '链接资源审核' : '链接审核' }}</h4>
          </div>
          <div class="actions-group" v-if="Object.keys(getLinksToAudit()).length > 0 && !isResourceReviewed">
            <button class="btn-custom btn-outline" @click="selectAllLinks">
              <i class="bi bi-check-all"></i> <span class="btn-text">全选</span>
            </button>
            <button class="btn-custom btn-outline" @click="deselectAllLinks">
              <i class="bi bi-square"></i> <span class="btn-text">取消全选</span>
            </button>
            <button 
              class="btn-custom link-group-approval-btn" 
              :disabled="selectedLinks.length === 0"
              @click="approveSelectedLinks"
            >
              <i class="bi bi-check-lg"></i> <span class="btn-text">批量批准</span>
            </button>
          </div>
        </div>
        <div class="card-body">
          <p v-if="(!resource.links || Object.keys(resource.links).length === 0) && 
                   (!isSupplementResource || Object.keys(getSupplementLinks()).length === 0)" 
             class="text-muted">
            该资源未提供任何链接
          </p>
          
          <!-- 原有资源的链接 (仅在补充资源时显示) -->
          <div v-if="isSupplementResource && originalLinks && Object.keys(originalLinks).length > 0">
            <h5 class="section-title">已有资源链接</h5>
            <div v-for="(categoryLinks, category) in originalLinks" :key="'existing-'+category" class="mb-4">
              <div class="link-category-card">
                <div class="link-category-header">
                  <h5>{{ getCategoryDisplay(category) }}</h5>
                </div>
                <div class="link-category-body">
                  <div v-for="(link, index) in categoryLinks" :key="'existing-link-'+index" class="link-item">
                    <div class="link-content">
                      <div class="link-url">
                        <i class="bi bi-link-45deg"></i>
                        <a :href="typeof link === 'string' ? link : link.url" target="_blank">{{ typeof link === 'string' ? link : link.url }}</a>
                          </div>
                      <div v-if="typeof link === 'object' && link.password" class="link-password">
                        <i class="bi bi-key"></i> {{ link.password }}
                          </div>
                      <div v-if="typeof link === 'object' && link.note" class="link-note">
                        <i class="bi bi-chat-left-text"></i> {{ link.note }}
                        </div>
                        </div>
                    <div class="link-badge">
                      <span class="badge-info">已有链接</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <h5 v-if="Object.keys(getLinksToAudit()).length > 0" class="section-title mt-4">补充链接</h5>
          </div>
          
          <!-- 补充链接审核 -->
          <div v-for="(categoryLinks, category) in linksToAudit" :key="'audit-'+category" class="mb-4">
            <div class="link-category-card">
              <div class="link-category-header">
                <h5>{{ getCategoryDisplay(category) }}</h5>
              </div>
              <div class="link-category-body">
                <div v-for="(link, index) in categoryLinks" :key="'link-'+index" class="link-item" 
                  :class="{
                    'link-approved': isLinkApproved(link),
                    'link-rejected': isLinkRejected(link)
                  }"
                >
                  <div class="link-content">
                    <div class="link-url">
                      <i class="bi bi-link-45deg"></i>
                      <a :href="typeof link === 'string' ? link : link.url" target="_blank">{{ typeof link === 'string' ? link : link.url }}</a>
                        </div>
                    <div v-if="typeof link === 'object' && link.password" class="link-password">
                      <i class="bi bi-key"></i> {{ link.password }}
                        </div>
                    <div v-if="typeof link === 'object' && link.note" class="link-note">
                      <i class="bi bi-chat-left-text"></i> {{ link.note }}
                      </div>
                  </div>
                  <div class="link-actions" v-if="!isResourceReviewed">
                    <button 
                      class="btn-custom btn-sm btn-outline" 
                      @click="toggleLinkSelection(category, index)"
                      :class="{'is-selected': isLinkSelected(category, index)}"
                    >
                      <i class="bi" :class="isLinkSelected(category, index) ? 'bi-check-square-fill' : 'bi-square'"></i>
                    </button>
                    <button 
                      class="btn-custom btn-sm link-approval-btn" 
                      @click="approveLink(typeof link === 'string' ? link : link.url)"
                      :disabled="isLinkRejected(link)"
                    >
                      <i class="bi bi-check-lg"></i> <span class="btn-text">{{ isLinkApproved(link) ? '已批准' : '批准' }}</span>
                    </button>
                    <button 
                      class="btn-custom btn-sm btn-accent" 
                      @click="rejectLink(typeof link === 'string' ? link : link.url)"
                      :disabled="isLinkApproved(link)"
                    >
                      <i class="bi bi-x-lg"></i> <span class="btn-text">{{ isLinkRejected(link) ? '已拒绝' : '拒绝' }}</span>
                    </button>
                  </div>
                  <div class="link-status" v-else>
                    <span v-if="isLinkApproved(link)" class="status-badge status-approved">已批准</span>
                    <span v-if="isLinkRejected(link)" class="status-badge status-rejected">已拒绝</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 审批意见 -->
      <div class="review-card">
        <div class="card-header">
          <h4><i class="bi bi-chat-left-quote"></i> 审批意见</h4>
        </div>
        <div class="card-body">
          <label for="reviewNotes" class="info-label">审核备注（可选）</label>
            <textarea
            class="custom-textarea"
              id="reviewNotes"
              v-model="reviewNotes"
              rows="3"
              placeholder="请输入审核意见或建议..."
              :disabled="isResourceReviewed"
            ></textarea>
        </div>
      </div>
      
      <!-- 最终审批按钮 -->
      <div class="review-card">
        <div class="card-body">
          <div class="action-bar">
            <router-link to="/admin" class="btn-custom btn-outline return-btn">
              <i class="bi bi-arrow-left"></i> <span class="btn-text">返回管理面板</span>
            </router-link>
            <div v-if="!isResourceReviewed">
              <button 
                class="btn-custom btn-primary" 
                :disabled="submitLoading"
                @click="finalizeApproval('approved')"
              >
                <div v-if="submitLoading" class="spinner"></div>
                <i class="bi bi-check-circle"></i>
                <span class="btn-text">{{ submitLoading ? '处理中...' : '结束审核' }}</span>
              </button>
            </div>
            <div v-else class="status-badge status-approved">
              <i class="bi bi-check-circle-fill"></i> 
              <span v-if="isSupplementResource">该补充内容已完成审核</span>
              <span v-else>该资源已完成审核</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 图片放大模态框 -->
  <div v-if="largeImageUrl" class="large-image-overlay" @click.self="closeLargeImage">
    <div class="large-image-container">
      <img :src="largeImageUrl" class="large-image" alt="放大图片" @click.stop />
      <button class="close-large-img" @click.stop="closeLargeImage">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { debugAuth } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const resourceId = route.params.id

const resource = ref({})
const reviewResult = ref({
  approvedLinks: [],
  rejectedLinks: [],
  approvedImages: [],
  rejectedImages: []
})
const loading = ref(true)
const error = ref(null)
const reviewNotes = ref('')
const submitLoading = ref(null)

// 新增: 是否为补充资源的标志
const isSupplementResource = ref(false)
// 新增: 存储补充的内容，方便区分原有内容和新提交内容
const supplementContent = ref({
  images: [],
  links: {}
})

// 图片放大查看相关
const largeImageUrl = ref(null)

// 字段审批状态
const fieldApproval = reactive({})
const fieldRejection = reactive({})

// 图片审批状态
const selectedImages = ref([])
const approvedImages = ref([])
const rejectedImages = ref([])

// 海报图片
const posterImage = ref(null)

// 链接审批状态
const selectedLinks = ref([]) // {category, index}
const approvedLinks = ref([]) // {category, index}
const rejectedLinks = ref([]) // {category, index}

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

// 在 setup 函数中添加新变量
const originalLinks = ref({});  // 存储原始链接
const supplementLinks = ref({});  // 存储补充链接

// 计算属性
const hasLinks = computed(() => {
  // 检查资源是否存在
  if (!resource.value) {
    return false
  }
  
  // 检查links字段是否初始化
  if (!resource.value.links) {
    return false
  }
  
  // 检查links是否为对象
  if (typeof resource.value.links !== 'object' || resource.value.links === null) {
    return false
  }
  
  // 获取所有链接分类
  const categories = Object.keys(resource.value.links)
  
  // 如果没有分类，返回false
  if (categories.length === 0) {
    return false
  }
  
  // 检查是否至少有一个分类有链接
  for (const category of categories) {
    const links = resource.value.links[category]
    
    // 如果链接存在且是非空数组或非空对象，返回true
    if (links) {
      if (Array.isArray(links) && links.length > 0) {
        return true
      } else if (typeof links === 'object' && Object.keys(links).length > 0) {
        return true
      } else if (typeof links === 'string' && links.trim() !== '') {
        return true
      }
    }
  }
  
  return false
})

// 检查资源是否已审核
const isResourceReviewed = computed(() => {
  // 检查资源对象是否存在
  if (!resource.value) {
    return false;
  }
  
  // 对于补充资源审核，检查supplement的状态
  if (isSupplementResource.value && resource.value.supplement) {
    // 只有当supplement的状态为pending时才表示待审核
    return resource.value.supplement.status !== 'pending';
  }
  
  // 对于原始资源审核，检查资源状态
  return resource.value.status === 'approved' || resource.value.status === 'rejected';
})

// 获取类型显示名称
const getCategoryDisplayName = (category) => {
  return categoryDisplayNames[category] || category
}

// 截断文本显示
const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 从服务器获取资源详情
const fetchResourceDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`/api/resources/${resourceId}`)
    resource.value = response.data
    
    console.log('获取的资源详情:', JSON.stringify(resource.value))
    
    // 初始化或更新 reviewResult
    if (response.data.reviewResult) {
      reviewResult.value = response.data.reviewResult;
    } else {
      reviewResult.value = {
        approvedLinks: [],
        rejectedLinks: [],
        approvedImages: [],
        rejectedImages: []
      };
    }
    
    // 检查是否为补充资源，并保存补充内容
    if (resource.value.supplement && resource.value.supplement.status === 'pending') {
      isSupplementResource.value = true
      console.log('检测到补充资源，补充内容:', JSON.stringify(resource.value.supplement))
      
      // 保存补充内容
      if (resource.value.supplement.images) {
        supplementContent.value.images = resource.value.supplement.images
        console.log('补充图片:', supplementContent.value.images)
      }
      
      if (resource.value.supplement.links) {
        supplementContent.value.links = resource.value.supplement.links
        console.log('补充链接:', JSON.stringify(supplementContent.value.links))
      }
      
      // 调用分离链接的方法
      separateLinks();
    }
    
    // 处理资源链接数据
    if (resource.value) {
      // 初始化链接字段
      if (!resource.value.links) {
        resource.value.links = {}
      }
      
      // 处理补充资源中的链接
      if (resource.value.supplement && resource.value.supplement.links) {
        mergeLinks(resource.value.links, resource.value.supplement.links)
      }
      
      // 处理value字段中的链接
      if (resource.value.value && typeof resource.value.value === 'object') {
        if (resource.value.value.links) {
          mergeLinks(resource.value.links, resource.value.value.links)
        } else {
          // 检查是否直接包含链接类别
          const potentialCategories = Object.keys(categoryDisplayNames)
          let foundDirectLinks = false
          
          potentialCategories.forEach(category => {
            if (resource.value.value[category]) {
              foundDirectLinks = true
              
              // 确保目标类别是数组
              if (!resource.value.links[category]) {
                resource.value.links[category] = []
              } else if (!Array.isArray(resource.value.links[category])) {
                resource.value.links[category] = [resource.value.links[category]]
              }
              
              // 添加链接
              const newLinks = Array.isArray(resource.value.value[category]) 
                ? resource.value.value[category]
                : [resource.value.value[category]]
              
              resource.value.links[category] = resource.value.links[category].concat(newLinks)
            }
          })
          
          // 如果没有找到直接的链接类别，尝试将整个value作为links处理
          if (!foundDirectLinks) {
            mergeLinks(resource.value.links, resource.value.value)
          }
        }
      }
      
      // 确保每个分类下的链接是数组
      Object.keys(resource.value.links).forEach(category => {
        const links = resource.value.links[category]
        if (!Array.isArray(links)) {
          resource.value.links[category] = links ? [links] : []
        }
        
        // 确保每个链接都是对象格式
        resource.value.links[category] = resource.value.links[category].map(link => {
          if (typeof link === 'string') {
            return { url: link }
          }
          return link
        })
      })
      
      // 如果资源已有海报图片，预先选择它
      if (resource.value.poster_image) {
        posterImage.value = resource.value.poster_image
      }
    }
    
  } catch (err) {
    console.error('获取资源详情失败:', err)
    error.value = '获取资源详情失败，请稍后重试'
    
    if (err.response && err.response.status === 401) {
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } finally {
    loading.value = false
  }
}

// 辅助函数：合并链接数据
const mergeLinks = (targetLinks, sourceLinks) => {
  if (!sourceLinks || typeof sourceLinks !== 'object') {
    return
  }
  
  Object.keys(sourceLinks).forEach(category => {
    const links = sourceLinks[category]
    if (!links || (!Array.isArray(links) && typeof links !== 'object')) {
      return
    }
    
    // 确保目标类别是数组
    if (!targetLinks[category]) {
      targetLinks[category] = []
    } else if (!Array.isArray(targetLinks[category])) {
      targetLinks[category] = [targetLinks[category]]
    }
    
    // 添加链接
    const newLinks = Array.isArray(links) ? links : [links]
    targetLinks[category] = targetLinks[category].concat(newLinks)
  })
}

// 切换字段审批状态
const toggleFieldApproval = (field) => {
  fieldApproval[field] = !fieldApproval[field]
  if (fieldApproval[field]) {
    fieldRejection[field] = false
  }
}

// 切换字段拒绝状态
const toggleFieldRejection = (field) => {
  fieldRejection[field] = !fieldRejection[field]
  if (fieldRejection[field]) {
    fieldApproval[field] = false
  }
}

// 切换图片选择状态
const toggleImageSelection = (image) => {
  if (!selectedImages || !selectedImages.value) {
    selectedImages.value = [];
  }
  
  const index = selectedImages.value.indexOf(image)
  if (index === -1) {
    selectedImages.value.push(image)
  } else {
    selectedImages.value.splice(index, 1)
  }
}

// 全选图片
const selectAllImages = () => {
  if (!resource || !resource.value || !resource.value.images) {
    return;
  }
  
  selectedImages.value = resource.value.images.filter(
    img => (!approvedImages || !approvedImages.value || !approvedImages.value.includes(img)) && 
           (!rejectedImages || !rejectedImages.value || !rejectedImages.value.includes(img))
  )
}

// 获取需要审核的图片 (对于补充资源，只返回补充的图片)
const getImagesToAudit = () => {
  if (isSupplementResource.value) {
    return supplementContent && supplementContent.value && supplementContent.value.images || [];
  } else {
    return resource && resource.value && resource.value.images || [];
  }
}

// 全选补充图片
const selectAllSupplementImages = () => {
  if (!supplementContent || !supplementContent.value || !supplementContent.value.images) {
    return;
  }
  
  selectedImages.value = supplementContent.value.images.filter(
    img => (!approvedImages || !approvedImages.value || !approvedImages.value.includes(img)) && 
           (!rejectedImages || !rejectedImages.value || !rejectedImages.value.includes(img))
  )
}

// 判断是否可以选择为海报图片
const canSelectAsPoster = (image) => {
  return approvedImages && approvedImages.value && approvedImages.value.includes && 
         approvedImages.value.includes(image) && 
         (!posterImage || !posterImage.value || posterImage.value !== image);
}

// 设置海报图片
const setPosterImage = (image) => {
  posterImage.value = image;
}

// 清除海报图片选择
const clearPosterImage = () => {
  posterImage.value = null;
}

// 批准单张图片
const approveImage = (image) => {
  if (!approvedImages || !approvedImages.value) {
    approvedImages.value = [];
  }
  
  if (!approvedImages.value.includes(image)) {
    approvedImages.value.push(image);
    console.log(`批准图片: ${image}, 当前批准图片列表长度: ${approvedImages.value.length}`);
    
    // 确保reviewResult中也记录了批准的图片
    if (!reviewResult.value) {
      reviewResult.value = {};
    }
    if (!reviewResult.value.approvedImages) {
      reviewResult.value.approvedImages = [];
    }
    if (!reviewResult.value.approvedImages.includes(image)) {
      reviewResult.value.approvedImages.push(image);
      console.log(`添加图片到reviewResult.approvedImages: ${image}, 当前长度: ${reviewResult.value.approvedImages.length}`);
    }
    
    // 如果图片在已拒绝列表中，将其移除
    if (rejectedImages && rejectedImages.value) {
      const index = rejectedImages.value.indexOf(image);
      if (index !== -1) {
        rejectedImages.value.splice(index, 1);
      }
    }
    
    // 从reviewResult的拒绝列表中移除
    if (reviewResult.value && reviewResult.value.rejectedImages) {
      const index = reviewResult.value.rejectedImages.indexOf(image);
      if (index !== -1) {
        reviewResult.value.rejectedImages.splice(index, 1);
      }
    }
    
    // 如果是第一张批准的图片且没有设置海报，自动设置为海报
    if (approvedImages.value.length === 1 && (!posterImage || !posterImage.value)) {
      posterImage.value = image;
    }
    
    // 保存审核状态
    saveReviewState();
  }
}

// 拒绝单张图片
const rejectImage = (image) => {
  if (!rejectedImages || !rejectedImages.value) {
    rejectedImages.value = [];
  }
  
  if (!rejectedImages.value.includes(image)) {
    rejectedImages.value.push(image);
    
    // 确保reviewResult中也记录了拒绝的图片
    if (!reviewResult.value) {
      reviewResult.value = {};
    }
    if (!reviewResult.value.rejectedImages) {
      reviewResult.value.rejectedImages = [];
    }
    if (!reviewResult.value.rejectedImages.includes(image)) {
      reviewResult.value.rejectedImages.push(image);
    }
    
    // 如果图片在已批准列表中，将其移除
    if (approvedImages && approvedImages.value) {
      const index = approvedImages.value.indexOf(image);
      if (index !== -1) {
        approvedImages.value.splice(index, 1);
      }
    }
    
    // 从reviewResult的批准列表中移除
    if (reviewResult.value && reviewResult.value.approvedImages) {
      const index = reviewResult.value.approvedImages.indexOf(image);
      if (index !== -1) {
        reviewResult.value.approvedImages.splice(index, 1);
      }
    }
    
    // 如果是海报图片，清除海报设置
    if (posterImage && posterImage.value && image === posterImage.value) {
      posterImage.value = null;
    }
    
    // 保存审核状态
    saveReviewState();
  }
}

// 批准选中图片
const approveSelectedImages = () => {
  if (selectedImages && selectedImages.value) {
    selectedImages.value.forEach(image => {
      approveImage(image);
    });
    selectedImages.value = [];
  }
}

// 拒绝选中图片
const rejectSelectedImages = () => {
  if (selectedImages && selectedImages.value) {
    selectedImages.value.forEach(image => {
      rejectImage(image);
    });
    selectedImages.value = [];
  }
}

// 取消全选
const deselectAllImages = () => {
  if (selectedImages) {
    selectedImages.value = []
  }
}

// 检查是否可以批准资源
const canApprove = () => {
  // 检查是否有必填字段被拒绝
  const requiredFields = ['title', 'title_en', 'resource_type']
  const anyRequiredFieldRejected = requiredFields.some(field => fieldRejection[field])
  
  return !anyRequiredFieldRejected
}

// 获取批准按钮文本
const getApproveButtonText = () => {
  if (!canApprove()) {
    return '请先处理所有必填字段'
  }
  return '批准资源'
}

// 链接选择相关方法
const toggleLinkSelection = (category, index) => {
  const linkId = `${category}-${index}`;
  const existingIndex = selectedLinks.value.findIndex(
    link => link.category === category && link.index === index
  );
  
  if (existingIndex === -1) {
    selectedLinks.value.push({ category, index });
  } else {
    selectedLinks.value.splice(existingIndex, 1);
  }
}

const isLinkSelected = (category, index) => {
  return selectedLinks.value.some(
    link => link.category === category && link.index === index
  );
}

// 检查链接是否被批准(针对链接对象)
const isLinkApproved = (link) => {
  if (!reviewResult || !reviewResult.value) {
    return false;
  }
  
  const linkUrl = typeof link === 'string' ? link : link.url;
  
  // 查找链接所属分类
  for (const category of Object.keys(linksToAudit.value)) {
    const links = linksToAudit.value[category];
    if (links && links.length > 0) {
      for (const l of links) {
        const currentUrl = typeof l === 'string' ? l : l.url;
        if (currentUrl === linkUrl) {
          // 生成链接标识符
          const linkIdentifier = `${category}:${linkUrl}`;
          
          // 检查是否在批准标识符列表中
          if (reviewResult.value.approvedLinkIdentifiers && 
              reviewResult.value.approvedLinkIdentifiers[linkIdentifier]) {
            return true;
          }
          
          // 兼容旧的检查方式
          if (reviewResult.value.approvedLinks && 
              reviewResult.value.approvedLinks.includes(linkUrl)) {
            return true;
          }
        }
      }
    }
  }
  
  return false;
};

// 检查链接是否被拒绝(针对链接对象)
const isLinkRejected = (link) => {
  if (!reviewResult || !reviewResult.value) {
    return false;
  }
  
  const linkUrl = typeof link === 'string' ? link : link.url;
  
  // 查找链接所属分类
  for (const category of Object.keys(linksToAudit.value)) {
    const links = linksToAudit.value[category];
    if (links && links.length > 0) {
      for (const l of links) {
        const currentUrl = typeof l === 'string' ? l : l.url;
        if (currentUrl === linkUrl) {
          // 生成链接标识符
          const linkIdentifier = `${category}:${linkUrl}`;
          
          // 检查是否在拒绝标识符列表中
          if (reviewResult.value.rejectedLinkIdentifiers && 
              reviewResult.value.rejectedLinkIdentifiers[linkIdentifier]) {
            return true;
          }
          
          // 兼容旧的检查方式
          if (reviewResult.value.rejectedLinks && 
              reviewResult.value.rejectedLinks.includes(linkUrl)) {
            return true;
          }
        }
      }
    }
  }
  
  return false;
};

// 原有方法：检查链接是否被批准(针对category和index)
const isLinkApprovedByIndex = (category, index) => {
  return approvedLinks.value.some(
    link => link.category === category && link.index === index
  );
}

// 原有方法：检查链接是否被拒绝(针对category和index)
const isLinkRejectedByIndex = (category, index) => {
  return rejectedLinks.value.some(
    link => link.category === category && link.index === index
  );
}

const isLinkApprovedOrRejected = (category, index) => {
  return isLinkApprovedByIndex(category, index) || isLinkRejectedByIndex(category, index);
}

// 链接批量操作
const selectAllLinks = () => {
  selectedLinks.value = [];
  
  // 遍历所有分类和链接
  if (resource.value && resource.value.links) {
    Object.keys(resource.value.links).forEach(category => {
      const categoryLinks = resource.value.links[category];
      if (Array.isArray(categoryLinks)) {
        categoryLinks.forEach((_, index) => {
          // 只选择未审核的链接（既不是已批准也不是已拒绝的）
          if (getLinkApprovalStatus(category, index) === 'pending') {
            selectedLinks.value.push({ category, index });
          }
        });
      }
    });
  }
  
  console.log(`已全选 ${selectedLinks.value.length} 个待审核链接`);
}

const deselectAllLinks = () => {
  selectedLinks.value = [];
}

const approveSelectedLinks = () => {
  // 跟踪已批准的链接数量
  let approvedCount = 0;
  
  selectedLinks.value.forEach(link => {
    if (!isLinkApprovedOrRejected(link.category, link.index)) {
      // 添加到approvedLinks数组
      approvedLinks.value.push({ ...link });
      
      try {
        // 获取链接URL
        const linkObj = getLinkObject(link.category, link.index);
        if (linkObj) {
          const linkUrl = typeof linkObj === 'string' ? linkObj : linkObj.url;
          
          // 确保reviewResult对象初始化
          if (!reviewResult.value) {
            reviewResult.value = {
              approvedLinks: [],
              rejectedLinks: [],
              approvedLinkIdentifiers: {},
              rejectedLinkIdentifiers: {}
            };
          }
          
          if (!reviewResult.value.approvedLinks) {
            reviewResult.value.approvedLinks = [];
          }
          
          if (!reviewResult.value.approvedLinkIdentifiers) {
            reviewResult.value.approvedLinkIdentifiers = {};
          }
          
          // 从拒绝列表中移除（如果存在）
          if (reviewResult.value.rejectedLinks && reviewResult.value.rejectedLinks.includes(linkUrl)) {
            reviewResult.value.rejectedLinks = reviewResult.value.rejectedLinks.filter(url => url !== linkUrl);
          }
          
          // 生成链接标识符并从拒绝标识符中移除
          const linkIdentifier = `${link.category}:${linkUrl}`;
          if (reviewResult.value.rejectedLinkIdentifiers && reviewResult.value.rejectedLinkIdentifiers[linkIdentifier]) {
            delete reviewResult.value.rejectedLinkIdentifiers[linkIdentifier];
          }
          
          // 添加到批准列表
          if (!reviewResult.value.approvedLinks.includes(linkUrl)) {
            reviewResult.value.approvedLinks.push(linkUrl);
            approvedCount++;
          }
          
          // 添加到批准标识符
          reviewResult.value.approvedLinkIdentifiers[linkIdentifier] = true;
        }
      } catch (error) {
        console.error('处理链接时出错:', error);
      }
    }
  });
  
  // 保存审核状态
  saveReviewState();
  
  // 显示批准数量
  if (approvedCount > 0) {
    console.log(`批量批准了 ${approvedCount} 个链接`);
  }
  
  // 清空选中链接
  selectedLinks.value = [];
}

const rejectSelectedLinks = () => {
  selectedLinks.value.forEach(link => {
    if (!isLinkApprovedOrRejected(link.category, link.index)) {
      rejectedLinks.value.push({ ...link });
    }
  });
  selectedLinks.value = [];
}

// 链接审核相关方法
const approveLink = (linkUrl) => {
  console.log(`尝试批准链接: ${linkUrl}`)
  
  if (!reviewResult.value) {
    reviewResult.value = {
      approvedLinks: [],
      rejectedLinks: []
    };
  }
  
  if (!reviewResult.value.approvedLinks) {
    reviewResult.value.approvedLinks = [];
  }
  
  // 如果链接已经在批准列表中，则不做任何操作
  if (reviewResult.value.approvedLinks.includes(linkUrl)) {
    console.log(`链接已经在批准列表中: ${linkUrl}`)
    return;
  }
  
  // 从拒绝列表中移除（如果存在）
  if (reviewResult.value.rejectedLinks && reviewResult.value.rejectedLinks.includes(linkUrl)) {
    reviewResult.value.rejectedLinks = reviewResult.value.rejectedLinks.filter(url => url !== linkUrl);
    console.log(`从拒绝列表中移除链接: ${linkUrl}`)
  }
  
  // 添加到批准列表
  reviewResult.value.approvedLinks.push(linkUrl);
  console.log(`链接已添加到批准列表: ${linkUrl}, 当前批准链接数量: ${reviewResult.value.approvedLinks.length}`)
  
  // 保存审核状态
  saveReviewState();
};

const rejectLink = (linkUrl) => {
  try {
    console.log('拒绝链接:', linkUrl);
    
    // 找到链接所在的分类
    let foundCategory = null;
    let foundLink = null;
    
    // 遍历所有分类查找链接
    for (const category of Object.keys(linksToAudit.value)) {
      const links = linksToAudit.value[category];
      if (links && links.length > 0) {
        for (const link of links) {
          const currentUrl = typeof link === 'string' ? link : link.url;
          if (currentUrl === linkUrl) {
            foundCategory = category;
            foundLink = link;
            console.log(`找到链接: ${linkUrl} 在分类 ${category} 中`);
            break;
          }
        }
        if (foundLink) break;
      }
    }
    
    if (!foundCategory || !foundLink) {
      console.warn(`未找到链接: ${linkUrl}`);
      return;
    }
    
    // 使用分类+URL作为唯一标识
    const linkIdentifier = `${foundCategory}:${linkUrl}`;
    
    // 创建新的审核结果对象（避免修改原始对象）
    const newReviewResult = {
      approvedLinks: reviewResult.value?.approvedLinks?.slice() || [],
      rejectedLinks: reviewResult.value?.rejectedLinks?.slice() || [],
      approvedLinkIdentifiers: reviewResult.value?.approvedLinkIdentifiers || {},
      rejectedLinkIdentifiers: reviewResult.value?.rejectedLinkIdentifiers || {},
      approvedImages: reviewResult.value?.approvedImages?.slice() || [],
      rejectedImages: reviewResult.value?.rejectedImages?.slice() || []
    };
    
    // 从批准列表中移除（如果存在）
    const approvedIndex = newReviewResult.approvedLinks.indexOf(linkUrl);
    if (approvedIndex !== -1) {
      newReviewResult.approvedLinks.splice(approvedIndex, 1);
      console.log(`将链接 ${linkUrl} 从批准列表中移除`);
    }
    
    // 从批准标识符中移除
    if (newReviewResult.approvedLinkIdentifiers && newReviewResult.approvedLinkIdentifiers[linkIdentifier]) {
      delete newReviewResult.approvedLinkIdentifiers[linkIdentifier];
      console.log(`将链接标识符 ${linkIdentifier} 从批准列表中移除`);
    }
    
    // 如果链接不在拒绝列表中，添加
    if (!newReviewResult.rejectedLinks.includes(linkUrl)) {
      newReviewResult.rejectedLinks.push(linkUrl);
      console.log(`将链接 ${linkUrl} 添加到拒绝列表，当前拒绝链接数量: ${newReviewResult.rejectedLinks.length}`);
    }
    
    // 添加到拒绝标识符
    if (!newReviewResult.rejectedLinkIdentifiers) {
      newReviewResult.rejectedLinkIdentifiers = {};
    }
    newReviewResult.rejectedLinkIdentifiers[linkIdentifier] = true;
    console.log(`将链接标识符 ${linkIdentifier} 添加到拒绝列表`);
    
    // 更新审核结果
    reviewResult.value = newReviewResult;
    console.log('更新后的审核结果:', reviewResult.value);
    
    // 保存状态到localStorage
    saveReviewState();
  } catch (error) {
    console.error('拒绝链接时出错:', error);
  }
};

// 批准所有链接
const approveAllLinks = async () => {
  try {
    // 确认操作
    if (!confirm('确定要批准所有链接吗？')) {
      return;
    }
    
    console.log('批准所有链接');
    
    // 创建新的审核结果对象
    const newReviewResult = {
      approvedLinks: reviewResult.value?.approvedLinks?.slice() || [],
      rejectedLinks: reviewResult.value?.rejectedLinks?.slice() || [],
      approvedLinkIdentifiers: reviewResult.value?.approvedLinkIdentifiers || {},
      rejectedLinkIdentifiers: reviewResult.value?.rejectedLinkIdentifiers || {},
      approvedImages: reviewResult.value?.approvedImages?.slice() || [],
      rejectedImages: reviewResult.value?.rejectedImages?.slice() || []
    };
    
    // 获取所有待审核的链接
    console.log('待审核的链接:', linksToAudit.value);
    
    // 将所有链接添加到批准列表
    for (const category of Object.keys(linksToAudit.value)) {
      const links = linksToAudit.value[category];
      if (links && links.length > 0) {
        for (const link of links) {
          const linkUrl = typeof link === 'string' ? link : link.url;
          
          // 生成链接标识符
          const linkIdentifier = `${category}:${linkUrl}`;
          
          // 从拒绝列表中移除（如果存在）
          const rejectIndex = newReviewResult.rejectedLinks.indexOf(linkUrl);
          if (rejectIndex !== -1) {
            newReviewResult.rejectedLinks.splice(rejectIndex, 1);
          }
          
          // 从拒绝标识符中移除
          if (newReviewResult.rejectedLinkIdentifiers && newReviewResult.rejectedLinkIdentifiers[linkIdentifier]) {
            delete newReviewResult.rejectedLinkIdentifiers[linkIdentifier];
          }
          
          // 如果链接不在批准列表中，添加
          if (!newReviewResult.approvedLinks.includes(linkUrl)) {
            newReviewResult.approvedLinks.push(linkUrl);
          }
          
          // 添加到批准标识符
          if (!newReviewResult.approvedLinkIdentifiers) {
            newReviewResult.approvedLinkIdentifiers = {};
          }
          newReviewResult.approvedLinkIdentifiers[linkIdentifier] = true;
          
          console.log(`批准链接: ${linkUrl} (${linkIdentifier})`);
        }
      }
    }
    
    // 更新审核结果
    reviewResult.value = newReviewResult;
    console.log('更新后的审核结果:', reviewResult.value);
    
    // 保存状态到localStorage
    saveReviewState();
  } catch (error) {
    console.error('批准所有链接时出错:', error);
  }
};

// 拒绝所有链接
const rejectAllLinks = async () => {
  try {
    // 确认操作
    if (!confirm('确定要拒绝所有链接吗？')) {
      return;
    }
    
    console.log('拒绝所有链接');
    
    // 创建新的审核结果对象
    const newReviewResult = {
      approvedLinks: reviewResult.value?.approvedLinks?.slice() || [],
      rejectedLinks: reviewResult.value?.rejectedLinks?.slice() || [],
      approvedLinkIdentifiers: reviewResult.value?.approvedLinkIdentifiers || {},
      rejectedLinkIdentifiers: reviewResult.value?.rejectedLinkIdentifiers || {},
      approvedImages: reviewResult.value?.approvedImages?.slice() || [],
      rejectedImages: reviewResult.value?.rejectedImages?.slice() || []
    };
    
    // 获取所有待审核的链接
    console.log('待审核的链接:', linksToAudit.value);
    
    // 将所有链接添加到拒绝列表
    for (const category of Object.keys(linksToAudit.value)) {
      const links = linksToAudit.value[category];
      if (links && links.length > 0) {
        for (const link of links) {
          const linkUrl = typeof link === 'string' ? link : link.url;
          
          // 生成链接标识符
          const linkIdentifier = `${category}:${linkUrl}`;
          
          // 从批准列表中移除（如果存在）
          const approveIndex = newReviewResult.approvedLinks.indexOf(linkUrl);
          if (approveIndex !== -1) {
            newReviewResult.approvedLinks.splice(approveIndex, 1);
          }
          
          // 从批准标识符中移除
          if (newReviewResult.approvedLinkIdentifiers && newReviewResult.approvedLinkIdentifiers[linkIdentifier]) {
            delete newReviewResult.approvedLinkIdentifiers[linkIdentifier];
          }
          
          // 如果链接不在拒绝列表中，添加
          if (!newReviewResult.rejectedLinks.includes(linkUrl)) {
            newReviewResult.rejectedLinks.push(linkUrl);
          }
          
          // 添加到拒绝标识符
          if (!newReviewResult.rejectedLinkIdentifiers) {
            newReviewResult.rejectedLinkIdentifiers = {};
          }
          newReviewResult.rejectedLinkIdentifiers[linkIdentifier] = true;
          
          console.log(`拒绝链接: ${linkUrl} (${linkIdentifier})`);
        }
      }
    }
    
    // 更新审核结果
    reviewResult.value = newReviewResult;
    console.log('更新后的审核结果:', reviewResult.value);
    
    // 保存状态到localStorage
    saveReviewState();
  } catch (error) {
    console.error('拒绝所有链接时出错:', error);
  }
};

// 最终提交审核结果
const finalizeApproval = async (status) => {
  try {
    submitLoading.value = true;
    
    // 打印当前状态
    console.log('----------提交前审核状态---------');
    console.log(`批准的图片数量: ${approvedImages.value?.length || 0}`);
    console.log(`审核结果中批准的图片数量: ${reviewResult.value?.approvedImages?.length || 0}`);
    console.log(`海报图片: ${posterImage.value || '未设置'}`);
    console.log('---------------------------');
    
    // 确保选择了海报图片
    if (!posterImage.value && approvedImages.value && approvedImages.value.length > 0) {
      // 如果没有选择海报图片但有已批准的图片，自动选择第一个批准的图片
      posterImage.value = approvedImages.value[0];
      console.log(`自动设置海报图片: ${posterImage.value}`);
    }
    
    // 确保approvedImages是一个有效的数组
    if (!approvedImages.value) {
      approvedImages.value = [];
    }
    
    // 确保rejectedImages是一个有效的数组
    if (!rejectedImages.value) {
      rejectedImages.value = [];
    }
    
    // 确保批准的图片列表与reviewResult.approvedImages保持同步，并排除已拒绝的图片
    if (reviewResult.value && reviewResult.value.approvedImages && reviewResult.value.approvedImages.length > 0) {
      // 从reviewResult.approvedImages同步到approvedImages，但排除已拒绝的图片
      for (const img of reviewResult.value.approvedImages) {
        if (!approvedImages.value.includes(img) && !(rejectedImages.value && rejectedImages.value.includes(img))) {
          approvedImages.value.push(img);
          console.log(`从reviewResult同步图片到approvedImages: ${img}`);
        }
      }
    }
    
    // 同步拒绝的图片列表
    if (reviewResult.value && reviewResult.value.rejectedImages && reviewResult.value.rejectedImages.length > 0) {
      for (const img of reviewResult.value.rejectedImages) {
        if (!rejectedImages.value.includes(img)) {
          rejectedImages.value.push(img);
          console.log(`从reviewResult同步图片到rejectedImages: ${img}`);
        }
      }
    }
    
    // 最后确保approvedImages中不包含rejectedImages中的图片
    if (rejectedImages.value && rejectedImages.value.length > 0) {
      approvedImages.value = approvedImages.value.filter(img => !rejectedImages.value.includes(img));
      console.log(`过滤后的批准图片数量: ${approvedImages.value.length}`);
    }
    
    // 准备链接数据
    const approvedLinkData = [];
    const rejectedLinkData = [];
    
    // 处理链接
    if (reviewResult && reviewResult.value) {
      // 详细打印待审核的链接数据
      console.log('待审核的链接数据:', JSON.stringify(linksToAudit.value));
      
      if (supplementContent.value && supplementContent.value.links) {
        console.log('原始补充链接数据:', JSON.stringify(supplementContent.value.links));
      }
      
      console.log('批准的链接数据:', JSON.stringify(reviewResult.value.approvedLinks || []));
      console.log('拒绝的链接数据:', JSON.stringify(reviewResult.value.rejectedLinks || []));
      
      // 处理已批准的链接
      if (reviewResult.value.approvedLinks && reviewResult.value.approvedLinks.length > 0) {
        for (const linkUrl of reviewResult.value.approvedLinks) {
          try {
            // 查找该链接所在的分类
            let foundCategory = null;
            let foundLink = null;
            
            // 首先在审核链接中查找
            for (const category of Object.keys(linksToAudit.value)) {
              const links = linksToAudit.value[category];
              if (links && links.length > 0) {
                for (const link of links) {
                  const currentUrl = typeof link === 'string' ? link : link.url;
                  if (currentUrl === linkUrl) {
                    foundCategory = category;
                    foundLink = link;
                    console.log(`在审核链接中找到批准的链接: ${linkUrl} 在分类 ${category} 中`);
                    break;
                  }
                }
                if (foundLink) break; // 找到后跳出循环
              }
            }
            
            // 如果在审核链接中没找到，再从原始补充内容中查找
            if (!foundLink && supplementContent.value && supplementContent.value.links) {
              for (const category of Object.keys(supplementContent.value.links)) {
                const links = supplementContent.value.links[category];
                if (links && links.length > 0) {
                  for (const link of links) {
                    const currentUrl = typeof link === 'string' ? link : link.url;
                    if (currentUrl === linkUrl) {
                      foundCategory = category;
                      foundLink = link;
                      console.log(`在原始补充内容中找到批准的链接: ${linkUrl} 在分类 ${category} 中`);
                      break;
                    }
                  }
                  if (foundLink) break; // 找到后跳出循环
                }
              }
            }
            
            if (foundCategory && foundLink) {
              const linkObj = typeof foundLink === 'string' ? { url: foundLink } : foundLink;
              const approvedLink = {
                category: foundCategory,
                url: linkObj.url,
                password: linkObj.password || '',
                note: linkObj.note || ''
              };
              console.log(`添加批准的链接到提交数据:`, approvedLink);
              approvedLinkData.push(approvedLink);
            } else {
              // 如果在所有来源中都找不到链接，但我们确实有链接URL，则创建一个基本数据结构
              // 这可能发生在某些特殊情况下，比如115链接等
              const urlParts = linkUrl.split('://');
              let category = 'others'; // 默认分类
              
              // 尝试通过URL判断分类
              if (urlParts.length > 1) {
                const domain = urlParts[1].split('/')[0];
                if (domain.includes('115.com')) {
                  category = '115';
                  console.log('通过URL识别为115链接');
                } else if (domain.includes('baidu.com')) {
                  category = 'baidu';
                  console.log('通过URL识别为百度网盘链接');
                } else if (domain.includes('aliyundrive')) {
                  category = 'aliyun';
                  console.log('通过URL识别为阿里云盘链接');
                }
                // 可以根据需要添加更多链接类型的识别
              }
              
              const approvedLink = {
                category: category,
                url: linkUrl,
                password: '',
                note: ''
              };
              console.log(`未找到链接对象，但创建了基本数据提交:`, approvedLink);
              approvedLinkData.push(approvedLink);
            }
          } catch (err) {
            console.error('处理批准链接时出错:', err);
          }
        }
      } else {
        console.log('没有批准的链接');
      }
      
      // 处理已拒绝的链接
      if (reviewResult.value.rejectedLinks && reviewResult.value.rejectedLinks.length > 0) {
        for (const linkUrl of reviewResult.value.rejectedLinks) {
          try {
            // 查找该链接所在的分类
            let foundCategory = null;
            let foundLink = null;
            
            // 首先在审核链接中查找
            for (const category of Object.keys(linksToAudit.value)) {
              const links = linksToAudit.value[category];
              if (links && links.length > 0) {
                for (const link of links) {
                  const currentUrl = typeof link === 'string' ? link : link.url;
                  if (currentUrl === linkUrl) {
                    foundCategory = category;
                    foundLink = link;
                    console.log(`在审核链接中找到拒绝的链接: ${linkUrl} 在分类 ${category} 中`);
                    break;
                  }
                }
                if (foundLink) break; // 找到后跳出循环
              }
            }
            
            // 如果在审核链接中没找到，再从原始补充内容中查找
            if (!foundLink && supplementContent.value && supplementContent.value.links) {
              for (const category of Object.keys(supplementContent.value.links)) {
                const links = supplementContent.value.links[category];
                if (links && links.length > 0) {
                  for (const link of links) {
                    const currentUrl = typeof link === 'string' ? link : link.url;
                    if (currentUrl === linkUrl) {
                      foundCategory = category;
                      foundLink = link;
                      console.log(`在原始补充内容中找到拒绝的链接: ${linkUrl} 在分类 ${category} 中`);
                      break;
                    }
                  }
                  if (foundLink) break; // 找到后跳出循环
                }
              }
            }
            
            if (foundCategory && foundLink) {
              const linkObj = typeof foundLink === 'string' ? { url: foundLink } : foundLink;
              const rejectedLink = {
                category: foundCategory,
                url: linkObj.url,
                password: linkObj.password || '',
                note: linkObj.note || ''
              };
              console.log(`添加拒绝的链接到提交数据:`, rejectedLink);
              rejectedLinkData.push(rejectedLink);
            } else {
              // 如果在所有来源中都找不到链接，但我们确实有链接URL，则创建一个基本数据结构
              const urlParts = linkUrl.split('://');
              let category = 'others'; // 默认分类
              
              // 尝试通过URL判断分类
              if (urlParts.length > 1) {
                const domain = urlParts[1].split('/')[0];
                if (domain.includes('115.com')) {
                  category = '115';
                  console.log('通过URL识别为115链接');
                } else if (domain.includes('baidu.com')) {
                  category = 'baidu';
                  console.log('通过URL识别为百度网盘链接');
                } else if (domain.includes('aliyundrive')) {
                  category = 'aliyun';
                  console.log('通过URL识别为阿里云盘链接');
                }
              }
              
              const rejectedLink = {
                category: category,
                url: linkUrl,
                password: '',
                note: ''
              };
              console.log(`未找到链接对象，但创建了基本数据提交:`, rejectedLink);
              rejectedLinkData.push(rejectedLink);
            }
          } catch (err) {
            console.error('处理拒绝链接时出错:', err);
          }
        }
      } else {
        console.log('没有拒绝的链接');
      }
    }
    
    console.log('批准的链接数据:', approvedLinkData);
    console.log('拒绝的链接数据:', rejectedLinkData);
    
    // 构建审批数据
    const approvalData = {
      status: 'approved', // 默认设为批准
      poster_image: posterImage.value,
      approved_images: approvedImages.value || [],
      rejected_images: rejectedImages.value || [],
      notes: reviewNotes.value,
      field_approvals: {},
      field_rejections: {},
      approved_links: approvedLinkData,
      rejected_links: rejectedLinkData
    };
    
    // 如果是补充资源，则不处理字段批准和拒绝
    if (!isSupplementResource.value) {
      // 添加字段审批状态
      Object.keys(fieldApproval).forEach(field => {
        if (fieldApproval[field]) {
          approvalData.field_approvals[field] = true;
        }
      });
      
      // 添加字段拒绝状态
      Object.keys(fieldRejection).forEach(field => {
        if (fieldRejection[field]) {
          approvalData.field_rejections[field] = true;
        }
      });
    }
    
    // 输出完整的审批链接数据
    console.log(`最终审批数据:`, JSON.stringify(approvalData));
    
    // 发送审批请求
    const response = await axios.put(`/api/resources/${resourceId}/approve`, approvalData);
    console.log(`审批响应:`, response.data);
    
    // 显示成功消息，区分补充资源和原始资源
    let successMsg = '';
    if (isSupplementResource.value) {
      successMsg = `补充内容审核完成！\n批准的图片: ${approvalData.approved_images.length} 张\n批准的链接: ${approvedLinkData.length} 个`;
    } else {
      successMsg = `资源审核完成！\n批准的图片: ${approvalData.approved_images.length} 张\n批准的链接: ${approvedLinkData.length} 个`;
    }
    alert(successMsg);
    
    // 清除localStorage中的审核状态
    localStorage.removeItem(`resource_review_${resourceId}`);
    console.log('已清除localStorage中的审核状态');
    
    // 跳转回管理员面板
    setTimeout(() => {
      router.push('/admin');
    }, 1500);
    
  } catch (err) {
    console.error('提交审批失败:', err);
    let errorMessage = '提交审批失败，请稍后重试';
    
    if (err.response && err.response.data && err.response.data.message) {
      errorMessage = err.response.data.message;
    }
    
    alert(errorMessage);
  } finally {
    submitLoading.value = null;
  }
}

// 获取海报图片名称
const getPosterImageName = () => {
  if (posterImage.value) {
    // 提取文件名用于显示
    const filename = posterImage.value.split('/').pop();
    return `【${filename}】`;
  }
  return '尚未设置 (请从已通过的图片中选择一张作为海报)';
}

// 显示大图
const showLargeImage = (imageUrl) => {
  largeImageUrl.value = imageUrl
  // 阻止页面滚动
  document.body.style.overflow = 'hidden'
}

// 打开图片查看器（与showLargeImage功能相同）
const openImageViewer = (imageUrl) => {
  showLargeImage(imageUrl);
}

// 关闭大图
const closeLargeImage = () => {
  largeImageUrl.value = null
  // 恢复页面滚动
  document.body.style.overflow = 'auto'
}

// 获取链接审批状态
const getLinkApprovalStatus = (category, index) => {
  // 检查是否已批准
  if (approvedLinks.value.some(l => l.category === category && l.index === index)) {
    return 'approved'
  }
  // 检查是否已拒绝
  if (rejectedLinks.value.some(l => l.category === category && l.index === index)) {
    return 'rejected'
  }
  // 默认为待审核
  return 'pending'
}

// 切换链接批准状态
const toggleLinkApproval = (category, index) => {
  // 如果已经批准，取消批准
  if (getLinkApprovalStatus(category, index) === 'approved') {
    approvedLinks.value = approvedLinks.value.filter(
      l => !(l.category === category && l.index === index)
    )
    return
  }
  
  // 移除拒绝状态（如果有）
  rejectedLinks.value = rejectedLinks.value.filter(
    l => !(l.category === category && l.index === index)
  )
  
  // 添加到批准列表
  approvedLinks.value.push({ category, index })
}

// 切换链接拒绝状态
const toggleLinkRejection = (category, index) => {
  // 如果已经拒绝，取消拒绝
  if (getLinkApprovalStatus(category, index) === 'rejected') {
    rejectedLinks.value = rejectedLinks.value.filter(
      l => !(l.category === category && l.index === index)
    )
    return
  }
  
  // 移除批准状态（如果有）
  approvedLinks.value = approvedLinks.value.filter(
    l => !(l.category === category && l.index === index)
  )
  
  // 添加到拒绝列表
  rejectedLinks.value.push({ category, index })
}

// 获取链接对象（处理不同格式）
const getLinkObject = (category, index) => {
  // 首先从待审核链接中查找
  if (linksToAudit.value && linksToAudit.value[category] && linksToAudit.value[category][index]) {
    const link = linksToAudit.value[category][index];
    // 如果是字符串，转换为对象
    if (typeof link === 'string') {
      return { url: link };
    }
    return link;
  }
  
  // 如果在待审核链接中找不到，从原始资源链接中查找
  if (!resource.value?.links?.[category]?.[index]) {
    return null;
  }
  
  const link = resource.value.links[category][index];
  
  // 如果是字符串，转换为对象
  if (typeof link === 'string') {
    return { url: link };
  }
  
  // 如果已经是对象，直接返回
  return link;
}

// 检查一个分类是否有被拒绝的链接
const hasRejectedLinks = (category) => {
  if (!resource.value || !resource.value.links || !resource.value.links[category]) {
    return false;
  }
  
  const links = resource.value.links[category];
  
  for (let i = 0; i < links.length; i++) {
    if (getLinkApprovalStatus(category, i) === 'rejected') {
      return true;
    }
  }
  
  return false;
}

// 添加在资源加载处理之后
// 分离原有链接和补充链接
const separateLinks = () => {
  if (isSupplementResource.value && resource.value.links) {
    // 存储原始链接
    originalLinks.value = {};
    supplementLinks.value = {};
    
    // 先处理原始资源的链接
    Object.keys(resource.value.links || {}).forEach(category => {
      // 对每个类别的链接进行处理
      const links = resource.value.links[category];
      if (links && links.length > 0) {
        // 检查是否存在于补充内容中
        const supplementCategoryLinks = supplementContent.value.links[category];
        
        if (supplementCategoryLinks) {
          // 有补充内容，需要分离
          originalLinks.value[category] = [];
          supplementLinks.value[category] = [];
          
          // 对每个链接检查是否在补充内容中
          links.forEach(link => {
            let found = false;
            
            // 检查链接是否在补充内容中
            for (const suppLink of supplementCategoryLinks) {
              // 确保比较时格式一致，提取URL进行比较
              const linkUrl = typeof link === 'string' ? link : link.url;
              const suppLinkUrl = typeof suppLink === 'string' ? suppLink : suppLink.url;
              
              if (linkUrl === suppLinkUrl) {
                found = true;
                // 使用原格式添加到补充链接中
                supplementLinks.value[category].push(link);
                break;
              }
            }
            
            // 如果不在补充内容中，则是原始链接
            if (!found) {
              originalLinks.value[category].push(link);
            }
          });
        } else {
          // 没有补充内容，全部是原始链接
          originalLinks.value[category] = [...links];
        }
      }
    });
    
    // 处理仅在补充内容中存在的类别
    Object.keys(supplementContent.value.links || {}).forEach(category => {
      if (!originalLinks.value[category]) {
        const links = supplementContent.value.links[category];
        if (links && links.length > 0) {
          supplementLinks.value[category] = [...links];
        }
      }
    });
  }
  
  // 在函数结束前添加日志
  console.log('分离后的原始链接:', JSON.stringify(originalLinks.value))
  console.log('分离后的补充链接:', JSON.stringify(supplementLinks.value))
};

// 获取链接类别显示名称
const getCategoryDisplay = (category) => {
  return categoryDisplayNames[category] || category;
};

// 获取需要审核的链接 - 使用计算属性缓存结果
const linksToAudit = computed(() => {
  if (isSupplementResource.value) {
    // 确保补充链接正确初始化
    const result = supplementLinks.value || {};
    // 只在调试模式下输出日志，减少日志量
    if (process.env.NODE_ENV === 'development') {
      console.debug("获取补充链接审核数据:", result);
    }
    return result;
  } else {
    return resource.value.links || {};
  }
});

// 替换原来的函数，使用计算属性
const getLinksToAudit = () => {
  return linksToAudit.value;
};

// 获取补充链接
const getSupplementLinks = () => {
  return supplementContent.value.links || {};
};

// 在onMounted前添加保存和恢复状态的函数
// 保存当前审核状态到localStorage
const saveReviewState = () => {
  try {
    const stateToSave = {
      resourceId: resourceId,
      reviewResult: reviewResult.value,
      approvedImages: approvedImages.value,
      rejectedImages: rejectedImages.value,
      posterImage: posterImage.value,
      reviewNotes: reviewNotes.value
    };
    localStorage.setItem(`resource_review_${resourceId}`, JSON.stringify(stateToSave));
    console.log('审核状态已保存到localStorage');
  } catch (error) {
    console.error('保存审核状态失败:', error);
  }
};

// 从localStorage恢复审核状态
const restoreReviewState = () => {
  try {
    const savedState = localStorage.getItem(`resource_review_${resourceId}`);
    if (savedState) {
      const parsedState = JSON.parse(savedState);
      
      // 验证是否是当前资源的状态
      if (parsedState.resourceId === resourceId) {
        reviewResult.value = parsedState.reviewResult || {};
        approvedImages.value = parsedState.approvedImages || [];
        rejectedImages.value = parsedState.rejectedImages || [];
        posterImage.value = parsedState.posterImage || null;
        reviewNotes.value = parsedState.reviewNotes || '';
        
        console.log('已从localStorage恢复审核状态');
      }
    }
  } catch (error) {
    console.error('恢复审核状态失败:', error);
  }
};

// 页面加载时获取资源详情
onMounted(async () => {
  // 确认用户已登录且是管理员
  const authStatus = debugAuth()
  
  if (!authStatus.isAuthenticated || !authStatus.isAdmin) {
    router.push('/login')
    return
  }
  
  await fetchResourceDetails()
  
  // 如果是补充资源，确保执行了separateLinks函数
  if (isSupplementResource.value) {
    console.log('页面挂载时检测到补充资源，执行separateLinks...')
    separateLinks();
  }
  
  // 从localStorage恢复审核状态
  restoreReviewState();
  
  // 显示图片和链接状态
  console.log('----------审核状态---------');
  console.log(`批准的图片数量: ${approvedImages.value?.length || 0}`);
  console.log(`审核结果中批准的图片数量: ${reviewResult.value?.approvedImages?.length || 0}`);
  if (approvedImages.value && approvedImages.value.length > 0) {
    console.log(`批准的图片列表: ${JSON.stringify(approvedImages.value)}`);
  }
  console.log(`补充资源中的图片数量: ${supplementContent.value?.images?.length || 0}`);
  if (supplementContent.value && supplementContent.value.images && supplementContent.value.images.length > 0) {
    console.log(`补充图片列表: ${JSON.stringify(supplementContent.value.images)}`);
  }
  console.log('---------------------------');
})
</script>

<style scoped>
/* 整体布局 */
.review-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 英雄区域 */
.review-hero {
  text-align: center;
  padding: 3rem 0;
  margin-bottom: 2rem;
  animation: fadeIn 0.8s ease-out;
  position: relative;
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

/* 审核卡片 */
.review-card {
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

.review-card:hover {
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

/* 操作按钮组样式 */
.actions-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* 卡片内容 */
.card-body {
  padding: 1.5rem;
}

/* 信息网格布局 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-weight: 600;
  color: var(--gray-color);
}

.info-value {
  color: var(--dark-color);
  word-break: break-word;
}

.id-badge {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-block;
}

.type-badge {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
  padding: 0.2rem 0.75rem;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-block;
}

/* 描述框 */
.description-box {
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
  border-radius: var(--border-radius);
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(99, 102, 241, 0.1);
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--dark-color);
}

/* 图片网格 */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.image-item {
  position: relative;
}

.image-card {
  position: relative;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  aspect-ratio: 1 / 1;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  display: block;
  cursor: zoom-in;
}

.image-card:hover img {
  transform: scale(1.1);
}

.image-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 10;
}

.image-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: var(--gray-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.select-btn {
  color: var(--primary-color);
}

.select-btn.is-selected {
  background: var(--primary-color);
  color: white;
}

.poster-btn {
  color: var(--accent-color);
}

.poster-btn.active {
  background: var(--accent-color);
  color: white;
}

.image-status {
  position: absolute;
  bottom: 0.5rem;
  left: 0.5rem;
  right: 0.5rem;
  display: flex;
  justify-content: center;
  z-index: 3;
}

.image-review-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  z-index: 2;
}

.image-review-actions button {
  flex: 1;
  border-radius: 0;
  padding: 0.5rem;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

/* 图片状态样式 */
.approved-image {
  border: 3px solid var(--success-color);
}

.rejected-image {
  border: 3px solid var(--accent-color);
}

.selected-image {
  border: 3px solid var(--primary-color);
}

.poster-image {
  border: 3px solid var(--secondary-color);
}

/* 链接样式 */
.link-category-card {
  border-radius: var(--border-radius);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(99, 102, 241, 0.1);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.link-category-card:hover {
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.link-category-header {
  padding: 1rem 1.25rem;
  background: rgba(99, 102, 241, 0.05);
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.link-category-header h5 {
  margin: 0;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 1.1rem;
}

.link-category-body {
  padding: 1rem;
}

.link-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-radius: var(--border-radius);
  background: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.75rem;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.link-item:last-child {
  margin-bottom: 0;
}

.link-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(3px);
}

.link-approved {
  border-left-color: var(--success-color);
}

.link-rejected {
  border-left-color: var(--accent-color);
}

.link-content {
  flex: 1;
  margin-right: 1rem;
}

.link-url {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  word-break: break-all;
}

.link-url a {
  color: var(--dark-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.link-url a:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.link-url i {
  color: var(--primary-color);
}

.link-password, .link-note {
  font-size: 0.9rem;
  color: var(--gray-color);
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.link-actions {
  display: flex;
  gap: 0.5rem;
}

.link-badge {
  white-space: nowrap;
}

/* 状态徽章 */
.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.status-approved {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.status-rejected {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
}

.status-warning {
  background: rgba(251, 191, 36, 0.1);
  color: #f59e0b;
}

.badge-info {
  background: rgba(6, 182, 212, 0.1);
  color: var(--secondary-color);
  padding: 0.25rem 0.5rem;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge-warning {
  background: rgba(251, 191, 36, 0.1);
  color: #f59e0b;
  padding: 0.25rem 0.5rem;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.35rem;
}

.badge-count {
  font-size: 0.9rem;
  color: var(--gray-color);
  font-weight: 400;
}

/* 按钮栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

/* 自定义按钮 */
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

.btn-success {
  background: var(--success-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
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

/* 自定义文本区域 */
.custom-textarea {
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: var(--border-radius);
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  outline: none;
  font-size: 0.95rem;
  line-height: 1.5;
  min-height: 120px;
  resize: vertical;
}

.custom-textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.9);
}

.custom-textarea::placeholder {
  color: rgba(99, 102, 241, 0.4);
}

.custom-textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: rgba(243, 244, 246, 0.7);
}

/* 图片放大模态框 */
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

/* 加载状态 */
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

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 错误消息 */
.error-message {
  background: rgba(244, 63, 94, 0.1);
  color: var(--accent-color);
  padding: 1rem;
  border-radius: var(--border-radius);
  margin: 2rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

.error-message i {
  font-size: 1.2rem;
}

/* 节标题 */
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
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

/* 响应式调整 */
@media (max-width: 992px) {
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .link-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .link-actions, .link-badge {
    margin-top: 1rem;
    align-self: flex-end;
  }

  /* 减少内边距提高可用空间 */
  .review-container {
    padding: 1rem;
  }
  
  .review-hero {
    padding: 2rem 0;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .card-header {
    padding: 1rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .info-grid {
    gap: 1rem;
  }
  
  /* 操作按钮组样式 */
  .actions-group {
    gap: 0.35rem;
    flex-wrap: nowrap;  /* 在中等屏幕下保持不换行 */
  }
}

@media (max-width: 768px) {
  .review-hero {
    padding: 2rem 0;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .card-header {
    flex-direction: row;
    gap: 0.75rem;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
  }
  
  /* 使用更高优先级的选择器确保标题完整显示 */
  .review-card .card-header h4,
  .card-header h4,
  h4 {
    font-size: 1.1rem !important;
    white-space: nowrap !important; /* 恢复不换行显示 */
    overflow: visible !important; 
    text-overflow: clip !important;
    max-width: 95% !important; /* 进一步增大标题显示区域 */
    line-height: 1.3 !important;
    flex-shrink: 1 !important; /* 允许标题区域在需要时收缩 */
  }
  
  /* 针对图片审核和链接审核卡片的特别处理 */
  .review-card:nth-child(2) .card-header h4,
  .review-card:nth-child(3) .card-header h4 {
    min-width: 0 !important;
    max-width: 100% !important;
    font-size: 1rem !important;
  }
  
  /* 为图标设置固定宽度，确保标题文字对齐 */
  .card-header h4 i {
    width: 1.3rem !important;
    text-align: center !important;
    margin-right: 0.2rem !important;
  }
  
  /* 重新调整按钮容器尺寸，为标题腾出空间 */
  .actions-group {
    width: auto;
    justify-content: flex-end;
    gap: 0.15rem !important;
    flex-wrap: nowrap;
    flex-shrink: 0 !important; /* 禁止按钮组收缩 */
    margin-left: 0.3rem !important; /* 增加与标题的间距 */
  }
  
  /* 确保底部操作栏始终水平布局 */
  .action-bar {
    flex-direction: row !important;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }
  
  /* 特别针对底部审批按钮区域，强制水平布局 */
  .review-card:last-of-type .card-body .action-bar {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
  }
  
  /* 移动端按钮仅显示图标，不显示文字 */
  .btn-text {
    display: none !important;
  }
  
  .btn-custom {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
    justify-content: center;
    border-radius: 50%;
  }
  
  .btn-custom i {
    font-size: 1.1rem;
    margin-right: 0;
  }
  
  /* 链接审批按钮特殊处理 - 强制一致的样式 */
  .link-approval-btn span,
  .btn-primary span,
  .return-btn span {
    display: none !important;
  }
  
  /* 确保所有按钮样式一致，包括返回和批准按钮 */
  .return-btn,
  .btn-primary {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
    border-radius: 50%;
    width: auto;
  }
}

@media (max-width: 576px) {
  .card-body {
    padding: 0.75rem;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.75rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  /* 使用更高优先级的选择器确保标题完整显示 */
  .review-card .card-header h4,
  .card-header h4,
  h4 {
    font-size: 0.9rem !important; /* 更小的字体 */
    max-width: 95% !important; /* 占用更多可用空间 */
    white-space: nowrap !important; /* 确保不换行 */
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.2 !important;
    flex-shrink: 1 !important;
  }
  
  /* 针对图片审核和链接审核卡片的特别处理 */
  .review-card:nth-child(2) .card-header h4,
  .review-card:nth-child(3) .card-header h4 {
    min-width: 0 !important;
    max-width: 100% !important;
    font-size: 0.85rem !important; /* 极小字体 */
  }
  
  /* 进一步缩小图标尺寸 */
  .card-header h4 i {
    font-size: 0.85rem !important;
    width: 1.1rem !important;
    text-align: center !important;
    margin-right: 0.1rem !important;
  }
  
  /* 优化操作组的按钮间距，更紧凑 */
  .actions-group {
    gap: 0.15rem;
    flex-shrink: 0 !important;
  }
  
  /* 调整按钮大小，更紧凑 */
  .btn-custom {
    padding: 0.35rem;
    min-width: 30px;
    height: 30px;
  }
  
  .btn-custom.btn-sm {
    min-width: 26px;
    height: 26px;
    padding: 0.3rem;
  }
  
  .btn-custom i {
    font-size: 0.9rem;
  }
  
  /* 确保底部操作栏保持水平且有适当间距 */
  .review-card .action-bar {
    gap: 0.5rem;
  }
  
  /* 确保带有徽章的按钮能正常显示 */
  .btn-custom .badge-count {
    display: inline-flex;
    position: absolute;
    top: -6px;
    right: -6px;
    min-width: 18px;
    height: 18px;
    border-radius: 50%;
    font-size: 0.7rem;
    align-items: center;
    justify-content: center;
  }
}

/* 特定按钮样式 */
.top-action-bar {
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.return-btn {
  background: rgba(255, 255, 255, 0.8);
  color: var(--primary-color);
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.return-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.approval-btn {
  background: var(--primary-gradient);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.25);
  border: none;
  position: relative;
  overflow: hidden;
}

.approval-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: 0.5s;
}

.approval-btn:hover::before {
  left: 100%;
}

.approval-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(99, 102, 241, 0.3);
}

/* 链接批准按钮样式 */
.link-approval-btn {
  background: linear-gradient(to right, #4f46e5, #6366f1);
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  border: none;
}

.link-approval-btn:hover {
  background: linear-gradient(to right, #4338ca, #4f46e5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.link-approval-btn:disabled {
  opacity: 0.6;
  background: linear-gradient(to right, #94a3b8, #cbd5e1);
  transform: none;
  box-shadow: none;
}

/* 批准所有链接按钮样式 */
.link-group-approval-btn {
  background: linear-gradient(to right, #4f46e5, #6366f1);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  border: none;
  position: relative;
  overflow: hidden;
}

.link-group-approval-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: 0.5s;
}

.link-group-approval-btn:hover::before {
  left: 100%;
}

.link-group-approval-btn:hover {
  background: linear-gradient(to right, #4338ca, #4f46e5);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(99, 102, 241, 0.4);
}

/* 图片批准按钮样式 */
.image-approval-btn {
  background: linear-gradient(to right, #4f46e5, #6366f1);
  color: white;
  font-weight: 600;
  border: none;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.image-approval-btn:hover {
  background: linear-gradient(to right, #4338ca, #4f46e5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.image-approval-btn:disabled {
  opacity: 0.6;
  background: linear-gradient(to right, #94a3b8, #cbd5e1);
  transform: none;
  box-shadow: none;
}

/* 响应式样式优化 */
@media (max-width: 992px) {
  .review-container {
    padding: 1rem;
  }
  
  .review-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.5rem;
  }
  
  .review-title {
    font-size: 1.8rem;
  }
  
  .review-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .review-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .review-sidebar {
    max-width: none;
    grid-row: 2;
  }
  
  .review-form {
    padding: 0;
  }
  
  .info-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .review-header {
    padding: 1.25rem;
    margin-bottom: 1rem;
  }
  
  .review-title {
    font-size: 1.6rem;
  }
  
  /* 修改卡片标题布局，保持水平布局 */
  .card-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .card-header h4 {
    font-size: 1.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 60%;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .card-header-actions {
    width: auto;
    justify-content: flex-end;
    margin-left: auto;
  }
  
  .actions-group {
    display: flex;
    flex-wrap: nowrap;
    gap: 0.5rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  /* 移动端按钮仅显示图标，隐藏文字 */
  .btn-text {
    display: none;
  }
  
  .btn-custom {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
    justify-content: center;
    border-radius: 50%;
  }
  
  .btn-custom i {
    font-size: 1.1rem;
    margin-right: 0;
  }
  
  .btn-custom.btn-sm {
    padding: 0.4rem;
    min-width: 32px;
    height: 32px;
  }
  
  /* 确保按钮图标居中 */
  .btn-custom .spinner {
    margin-right: 0;
  }
  
  .btn-group {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .btn-group .btn-custom {
    flex: 0 0 auto;
    min-width: auto;
  }
  
  .textarea-wrapper {
    min-height: 120px;
  }
  
  .custom-textarea {
    min-height: 120px;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  /* 改善图片操作按钮在移动端的可用性 */
  .image-actions {
    opacity: 1;
  }
  
  .image-btn {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
  
  /* 优化链接表格在移动端的显示 */
  .links-table {
    overflow-x: auto;
  }
  
  /* 特殊按钮处理 */
  .return-btn {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
  }
  
  .link-approval-btn, 
  .link-group-approval-btn,
  .image-approval-btn {
    padding: 0.5rem;
    border-radius: 50%;
  }
}

@media (max-width: 576px) {
  .review-header {
    padding: 1rem;
  }
  
  .review-title {
    font-size: 1.4rem;
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
  
  /* 调整表单元素样式 */
  .form-label {
    font-size: 0.9rem;
    margin-bottom: 0.35rem;
  }
  
  /* 调整操作按钮 */
  .btn-custom {
    padding: 0.45rem;
    font-size: 0.85rem;
    min-width: 32px;
    height: 32px;
  }
  
  .btn-custom.btn-sm {
    min-width: 28px;
    height: 28px;
    padding: 0.35rem;
  }
  
  .btn-custom i {
    font-size: 0.9rem;
  }
  
  /* 批量操作按钮优化 */
  .actions-group {
    gap: 0.25rem;
  }
  
  /* 增强表格可读性 */
  .links-table thead {
    display: none;
  }
  
  .links-table tbody tr {
    display: flex;
    flex-direction: column;
    padding: 0.75rem;
    border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  }
  
  .links-table td {
    display: flex;
    padding: 0.5rem 0;
    border: none;
  }
  
  .links-table td::before {
    content: attr(data-label);
    font-weight: 600;
    min-width: 80px;
    margin-right: 0.5rem;
    color: var(--gray-color);
  }
  
  /* 优化图片网格 */
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.75rem;
  }
  
  /* 调整数据项布局 */
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-value {
    font-size: 0.95rem;
  }
  
  /* 优化描述框 */
  .description-box {
    font-size: 0.9rem;
    padding: 0.75rem;
    max-height: 150px;
  }
  
  /* 批量操作按钮优化 */
  .batch-operations {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .batch-operations .btn-custom {
    flex: 1;
    min-width: calc(50% - 0.5rem);
  }
  
  /* 图片预览模态框优化 */
  .modal-image-container {
    max-width: 95vw;
  }
  
  .preview-large-image {
    max-height: 80vh;
  }
  
  .image-close-btn {
    right: 0;
    top: -40px;
  }
}

/* 特别针对底部审批按钮区域 */
.review-card:last-of-type .card-body .action-bar {
  flex-direction: row;
  flex-wrap: nowrap;
}

@media (max-width: 768px) {
  .review-hero {
    padding: 2rem 0;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .card-header {
    flex-direction: row;
    gap: 0.75rem;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
  }
  
  .card-header h4 {
    font-size: 1.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 70%; /* 增大标题显示区域 */
  }
  
  .actions-group {
    width: auto;
    justify-content: flex-end;
    gap: 0.35rem;
    flex-wrap: nowrap;  /* 在移动屏幕下保持不换行 */
  }
  
  /* 确保底部操作栏始终水平布局 */
  .action-bar {
    flex-direction: row !important;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }
  
  /* 特别针对底部审批按钮区域，强制水平布局 */
  .review-card:last-of-type .card-body .action-bar {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
  }
  
  /* 移动端按钮仅显示图标，不显示文字 */
  .btn-text {
    display: none !important;
  }
  
  .btn-custom {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
    justify-content: center;
    border-radius: 50%;
  }
  
  .btn-custom i {
    font-size: 1.1rem;
    margin-right: 0;
  }
  
  /* 链接审批按钮特殊处理 - 强制一致的样式 */
  .link-approval-btn span,
  .btn-primary span,
  .return-btn span {
    display: none !important;
  }
  
  /* 确保所有按钮样式一致，包括返回和批准按钮 */
  .return-btn,
  .btn-primary {
    padding: 0.5rem;
    min-width: 38px;
    height: 38px;
    border-radius: 50%;
    width: auto;
  }
}
</style> 