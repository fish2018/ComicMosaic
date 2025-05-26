import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import { isAuthenticated } from '../utils/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/resource/:id',
    name: 'ResourceDetail',
    component: () => import('../views/ResourceDetail.vue')
  },
  {
    path: '/submit',
    name: 'SubmitResource',
    component: () => import('../views/SubmitResource.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/resource-review/:id',
    name: 'ResourceReview',
    component: () => import('../views/ResourceReview.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫，检查是否需要登录
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated()) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 