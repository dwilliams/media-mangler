import Vue from 'vue'
import VueMaterial from 'vue-material'
import axios from 'axios'
import VueAxios from 'vue-axios'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

import App from './App.vue'

Vue.config.productionTip = false

Vue.use(VueAxios, axios)
Vue.use(VueMaterial)

new Vue({
  render: h => h(App),
}).$mount('#app')
