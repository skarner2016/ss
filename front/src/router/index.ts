import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        {
          path: '',
          name: 'Login',
          component: () => import('@/pages/Login.vue'),
        },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        {
          path: '',
          name: 'PostList',
          component: () => import('@/pages/PostList.vue'),
        },
        {
          path: 'post/create',
          name: 'PostCreate',
          component: () => import('@/pages/PostCreate.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'post/:id',
          name: 'PostDetail',
          component: () => import('@/pages/PostDetail.vue'),
        },
        {
          path: 'post/:id/edit',
          name: 'PostEdit',
          component: () => import('@/pages/PostEdit.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'user/:id',
          name: 'UserProfile',
          component: () => import('@/pages/UserProfile.vue'),
        },
        {
          path: 'favorites',
          name: 'Favorites',
          component: () => import('@/pages/Favorites.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
