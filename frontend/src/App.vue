<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px">
      <el-menu router :default-active="route.path">
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>Projects</span>
        </el-menu-item>
        <el-menu-item index="/tasks/new">
          <el-icon><Plus /></el-icon>
          <span>New Task</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>Tasks</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Folder, Plus, List } from '@element-plus/icons-vue'
const route = useRoute()
</script>
