<template>
  <div>
    <md-progress-bar md-mode="indeterminate" v-if="loading"></md-progress-bar>
    <md-table v-model="searched" md-sort="id" md-sort-order="asc" md-fixed-header md-height="78vh">
      <md-table-toolbar>
        <div class="md-toolbar-section-start">
          <h1 class="md-title">Files</h1>
        </div>

        <md-field md-clearable class="md-toolbar-section-end">
          <md-input placeholder="Search by name..." v-model="search" @input="searchOnTable" />
        </md-field>
      </md-table-toolbar>

      <md-table-empty-state md-label="No files found" :md-description="`No file found for this '${search}' query.`">
        <!--<md-button class="md-primary md-raised" @click="newUser">Create New User</md-button>-->
      </md-table-empty-state>

      <md-table-row slot="md-table-row" slot-scope="{ item }" :class="getClass(item)">
        <md-table-cell md-label="ID" md-sort-by="id" md-numeric>{{ item.id }}</md-table-cell>
        <md-table-cell md-label="Name" md-sort-by="name">{{ item.name }}</md-table-cell>
        <md-table-cell md-label="Type" md-sort-by="file_type">{{ item.file_type }}</md-table-cell>
        <md-table-cell md-label="Size" md-sort-by="size_bytes">{{ getReadableFileSizeString(item.size_bytes) }}</md-table-cell>
        <md-table-cell md-label="Media Count" md-sort-by="size">{{ item.medias_count }}</md-table-cell>
      </md-table-row>
    </md-table>
  </div>
</template>

<style lang="scss" scoped>
  .md-table-toolbar {
    height: 50;
    max-height: 50px;
    min-height: 50px;
  }

  .md-table-cell {
    height: auto;
  }

  .md-field {
    max-width: 300px;
  }

  .low-count {
    background-color: pink;
  }
</style>

<script>
  const toLower = text => {
    return text.toString().toLowerCase()
  }

  const searchByName = (items, term) => {
    if (term) {
      return items.filter(item => toLower(item.name).includes(toLower(term)))
    }
    return items
  }

  export default {
    name: 'filetable',
    data: () => ({
      info: [],
      loading: false,
      search: null,
      searched: []
    }),
    mounted () {
      this.loading = true;
      this.axios
        .get('http://localhost:5042/api/files/')
        .then(response => (this.updateData(response.data)));
    },
    methods: {
      getClass (item) {
        if(item.medias_count < 2) {
          return 'low-count';
        }
      },
      searchOnTable () {
        this.searched = searchByName(this.info, this.search)
      },
      updateData (tmp_data) {
        this.info = tmp_data;
        this.searchOnTable();
        this.loading = false;
      },
      getReadableFileSizeString (bytes) {
        var i = Math.floor(Math.log(bytes) / Math.log(1024));
        var sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        return (bytes / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + sizes[i];
      }
    }
  }
</script>