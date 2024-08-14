"use strict";

const UPLOAD_PAGE = "upload";
const ADD_URL_PAGE = "add_url";

const application = Vue.createApp({
  mounted() {
    this.updateDocuments();
  },

  data() {
    return {
      selectedPage: UPLOAD_PAGE,
      selectedFile: null,
      selectedUrl: "",
      documents: [],
      loading: false,
      message: "",
    };
  },

  methods: {
    setUploadPage() {
      this.selectedPage = UPLOAD_PAGE;
    },

    setAddUrlPage() {
      this.selectedPage = ADD_URL_PAGE;
    },

    showUploadPage() {
      return this.selectedPage === UPLOAD_PAGE;
    },

    showAddUrlPage() {
      return this.selectedPage === ADD_URL_PAGE;
    },

    updateDocuments() {
      fetch("/api/select", { method: "POST" })
        .then((response) => response.json())
        .then((result) => {
          if (result.success) {
            this.documents = result.documents;
          } else {
            this.documents = [];
          }
        });
    },

    uploadFile() {
      this.loading = true;

      const data = new FormData();
      data.append("file", this.selectedFile);

      fetch("/upload", {
        method: "POST",
        body: data,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            this.message = "";
          } else {
            this.message = data.message;
          }
        })
        .finally(() => (this.loading = false));
    },

    addUrl() {
      this.loading = true;

      fetch("/add_url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: this.selectedUrl }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            this.message = "";
          } else {
            this.message = data.message;
          }
        })
        .finally(() => (this.loading = false));
    },

    async removeDocument(document) {
      if (!confirm(`Do you want to remove file \`${document.filename}\`?`)) {
        return;
      }

      const response = await fetch("/api/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uuid: document.uuid }),
      })
        .then((response) => response.json())
        .then((data) => {
          this.updateDocuments();

          if (response.success) {
            this.message = "";
          } else {
            this.message = response.message;
          }
        });
    },

    fileChange(event) {
      if (event.target.files.length > 0) {
        this.selectedFile = event.target.files[0];
      }
    },

    fileName() {
      if (this.selectedFile !== null) {
        return this.selectedFile.name;
      } else {
        return "";
      }
    },

    fileEmpty() {
      return this.selectedFile === null;
    },

    urlValid() {
      return (
        this.selectedUrl.startsWith("http://") ||
        this.selectedUrl.startsWith("https://")
      );
    },

    documentLink(document) {
      return "/download/" + document.uuid;
    },

    documentClass(document) {
      switch (document.mimetype) {
        case "application/pdf":
          return "file pdf";

        case "text/plain":
          return "file alternate";

        case "image/jpeg":
        case "image/png":
          return "file image";

        default:
          return "file";
      }
    },
  },
});

application.mount("#app");
