(function () {
  "use strict";

  const API_BASE = "https://web-production-65d144.up.railway.app"; // ← update after Railway deploy

  // Icon map matching the backend ICON_MAP
  const ICONS = {
    "Data Sheet":   "fa-file-pdf",
    "Manual":       "fa-book",
    "Certificate":  "fa-certificate",
    "Drawing":      "fa-drafting-compass",
    "Brochure":     "fa-newspaper",
    "Installation": "fa-tools",
    "Compliance":   "fa-shield-alt",
    "Document":     "fa-file-alt",
  };

  function getIcon(docType) {
    return ICONS[docType] || "fa-file-alt";
  }

  function injectFontAwesome() {
    if (document.querySelector('link[href*="font-awesome"]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css";
    document.head.appendChild(link);
  }

  function injectStyles() {
    const style = document.createElement("style");
    style.textContent = `
      .tesnet-docs-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        padding: 16px 0;
      }
      .tesnet-doc-tile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        border: 1px solid #ddd;
        border-radius: 6px;
        text-decoration: none;
        color: #333;
        background: #fafafa;
        transition: background 0.15s, border-color 0.15s;
        min-width: 180px;
      }
      .tesnet-doc-tile:hover {
        background: #f0f4ff;
        border-color: #5b8ef7;
        color: #1a3fa8;
      }
      .tesnet-doc-tile i {
        font-size: 1.4rem;
        color: #c0392b;
        flex-shrink: 0;
      }
      .tesnet-doc-tile .tesnet-doc-info {
        display: flex;
        flex-direction: column;
      }
      .tesnet-doc-tile .tesnet-doc-label {
        font-weight: 600;
        font-size: 0.9rem;
      }
      .tesnet-doc-tile .tesnet-doc-type {
        font-size: 0.75rem;
        color: #888;
      }
    `;
    document.head.appendChild(style);
  }

  function buildTabContent(documents) {
    const grid = document.createElement("div");
    grid.className = "tesnet-docs-grid";

    documents.forEach(function (doc) {
      const a = document.createElement("a");
      a.href = doc.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.className = "tesnet-doc-tile";

      const icon = document.createElement("i");
      icon.className = "fas " + getIcon(doc.doc_type);

      const info = document.createElement("div");
      info.className = "tesnet-doc-info";

      const label = document.createElement("span");
      label.className = "tesnet-doc-label";
      label.textContent = doc.label;

      const type = document.createElement("span");
      type.className = "tesnet-doc-type";
      type.textContent = doc.doc_type;

      info.appendChild(label);
      info.appendChild(type);
      a.appendChild(icon);
      a.appendChild(info);
      grid.appendChild(a);
    });

    return grid;
  }

  function injectTab(documents) {
    // --- Tab link ---
    const tabList = document.querySelector(".tabs") || document.querySelector("[data-tab]");
    if (!tabList) {
      console.warn("[tesnet-docs] Could not find tab list element");
      return;
    }

    const li = document.createElement("li");
    li.className = "tab";

    const a = document.createElement("a");
    a.className = "tab-title";
    a.href = "#tab-documents";
    a.setAttribute("data-tab", "tab-documents");
    a.textContent = "Documents (" + documents.length + ")";

    li.appendChild(a);
    tabList.appendChild(li);

    // --- Tab content panel ---
    const tabContents =
      document.querySelector(".tabs-contents") ||
      document.querySelector(".tab-content")?.parentElement;

    if (!tabContents) {
      console.warn("[tesnet-docs] Could not find tab contents container");
      return;
    }

    const panel = document.createElement("div");
    panel.className = "tab-content";
    panel.id = "tab-documents";
    panel.setAttribute("data-tab-content", "tab-documents");
    panel.appendChild(buildTabContent(documents));

    tabContents.appendChild(panel);

    // Trigger BigCommerce tab re-init if available
    if (window.$ && $.fn.tabs) {
      try { $(".tabs").tabs("refresh"); } catch (e) { /* ignore */ }
    }
  }

  function init() {
    const container = document.getElementById("tesnet-docs");
    if (!container) return;

    const sku = container.getAttribute("data-sku");
    if (!sku) return;

    injectFontAwesome();
    injectStyles();

    fetch(API_BASE + "/api/docs?sku=" + encodeURIComponent(sku))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.documents && data.documents.length > 0) {
          injectTab(data.documents);
        }
      })
      .catch(function (err) {
        console.error("[tesnet-docs] Failed to load documents:", err);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
