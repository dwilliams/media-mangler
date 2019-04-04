<template>
  <div class="page-container">
    <md-app md-waterfall md-mode="fixed">
      <md-app-toolbar class="md-primary">
        <span class="md-title">Media Mangler</span>
      </md-app-toolbar>

      <md-app-drawer md-permanent="clipped">
        <md-list>
          <md-list-item v-on:click="currentView = 'dashboardpage'">
            <md-icon>dashboard</md-icon>
            <span class="md-list-item-text">Dashboard</span>
          </md-list-item>

          <md-list-item v-on:click="currentView = 'mediatable'">
            <md-icon>dns</md-icon>
            <span class="md-list-item-text">Media</span>
          </md-list-item>

          <md-list-item v-on:click="currentView = 'filetable'">
            <md-icon>insert_drive_file</md-icon>
            <span class="md-list-item-text">Files</span>
          </md-list-item>
        </md-list>
      </md-app-drawer>

      <md-app-content>
        <!--<mediatable></mediatable>-->
        <transition name="component-fade" mode="out-in">
          <component v-bind:is="currentView"></component>
        </transition>
      </md-app-content>
    </md-app>
  </div>
</template>

<style lang="scss" scoped>
  .md-app {
  }

  .md-drawer {
    width: 180px;
    /*max-width: calc(100vw - 125px);*/
  }

  .md-app-content {
    min-height: calc(100vh - 64px); /* 100 view height minus header and footer and borders */
  }
</style>

<script>
import dashboardpage from './dashboardpage.vue';
import filetable from './filetable.vue';
import mediatable from './mediatable.vue';

export default {
  name: 'normal',
  components: {
    dashboardpage,
    filetable,
    mediatable
  },
  data: function() {
    return {
      currentView: 'dashboardpage'
    }
  }
}
</script>