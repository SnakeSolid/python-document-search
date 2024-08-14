"use strict";

const application = Vue.createApp({
  mounted() {
    this.updateLanguages();
  },

  data() {
    return {
      languages: ["English"],
      selectedLanguage: "English",
      query: "",
      resultQuery: "",
      resultText: "",
      resultDocuments: [],
      resultImages: [],
      loading: false,
    };
  },

  methods: {
    queryEmpty() {
      return this.query.trim() === "";
    },

    showResult() {
      return this.resultText !== "";
    },

    showDocuments() {
      return this.resultDocuments.length > 0;
    },

    showImages() {
      return this.resultImages.length > 0;
    },

    documentLink(document) {
      return "/download/" + document.uuid;
    },

    documentId(document) {
      return "source_" + document.index;
    },

    resultHtml() {
      const markdown = markdownit().use((markdown) => {
        markdown.core.ruler.after("inline", "semantic", function (state) {
          const tokens = state.tokens;

          for (const token of tokens) {
            if (token.type === "heading_open") {
              token.attrPush(["class", "ui header"]);
            } else if (token.type === "bullet_list_open") {
              token.attrPush(["class", "ui list"]);
            } else if (token.type === "ordered_list_open") {
              token.attrPush(["class", "ui list"]);
            } else if (token.type === "table_open") {
              token.attrPush(["class", "ui compact striped table"]);
            }
          }
        });
      });

      return markdown.render(this.resultText);
    },

    updateLanguages() {
      fetch("/api/languages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: this.selectedLanguage,
          query: this.query,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            this.languages = data.languages;
          }
        });
    },

    search() {
      this.loading = true;

      fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: this.selectedLanguage,
          query: this.query,
        }),
      })
        .then((data) => data.json())
        .then((data) => {
          if (data.success) {
            this.resultQuery = data.result.query;
            this.resultText = data.result.text;
            this.resultDocuments = data.result.documents;
            this.resultImages = data.result.images;
          } else {
            this.resultQuery = "No results";
            this.resultText = "";
            this.resultDocuments = [];
            this.resultImages = [];
          }
        })
        .finally(() => (this.loading = false));
    },
  },
});

application.mount("#app");
