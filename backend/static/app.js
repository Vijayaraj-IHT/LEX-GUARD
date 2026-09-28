/* =========================================================
   LexGuard — front-end prototype application logic
   Vanilla JavaScript only. No frameworks, no build step.
   Sections: state, sample data, navigation, render functions,
   filters, form validation, exactly-one-owner validation,
   case editor row management, review-status helpers,
   SHA-256 demonstration, diagram zoom controls,
   accessibility helpers, initialization.
   ========================================================= */

(function () {
  "use strict";

  /* ================= STATE ================= */

  const ROUTES = [
    "home", "dashboard", "drafts", "sources", "case-editor",
    "court-learning", "review-status", "hash-demo", "diagrams", "about"
  ];

  const state = {
    route: "home",
    draftFilter: { text: "", status: "" },
    selectedDraftId: null,
    caseTab: "core",
    caseRows: { parties: [], provisions: [], issues: [], actions: [] },
    rowSeq: 1,
    workflowSteps: [],
    diagramZoom: { er: 1, schema: 1 },
    lightboxZoom: 1,
    lightboxTarget: null
  };

  /* ================= SAMPLE PLACEHOLDER DATA ================= */

  const REVIEW_STATUSES = [
    { value: "draft", label: "draft", meaning: "Incomplete or unreviewed" },
    { value: "source_linked", label: "source_linked", meaning: "An identified official source is recorded" },
    { value: "metadata_reviewed", label: "metadata_reviewed", meaning: "Metadata checked against the source" },
    { value: "file_verified", label: "file_verified", meaning: "A stable source file has an integrity hash" },
    { value: "needs_correction", label: "needs_correction", meaning: "A problem requires correction" },
    { value: "superseded", label: "superseded", meaning: "A newer record or version exists" },
    { value: "withdrawn", label: "withdrawn", meaning: "Not active reviewed content" }
  ];

  const DASHBOARD_METRICS = [
    { label: "Legacy draft records", value: "5" },
    { label: "Official-source reviewed records", value: "0" },
    { label: "Substantive automated tests", value: "16" },
    { label: "Current database target", value: "SQLite" },
    { label: "Approved logical tables", value: "13" },
    { label: "Current phase", value: "1–3 foundation" }
  ];

  const MISSING_INFO_FIELDS = [
    "Official source URL", "Source publisher", "Retrieval date",
    "Citation", "Review status", "Last-reviewed date"
  ];

  // Five neutral quarantined draft records. No real case names, citations,
  // judgments, holdings, courts, parties, dates, or sources are invented here.
  const draftRecords = [1, 2, 3, 4, 5].map(function (n) {
    const statusCycle = ["draft", "source_linked", "needs_correction", "draft", "metadata_reviewed"];
    const missingCycle = [
      MISSING_INFO_FIELDS,
      ["Retrieval date", "Citation", "Review status", "Last-reviewed date"],
      ["Source publisher", "Citation", "Last-reviewed date"],
      MISSING_INFO_FIELDS,
      ["Last-reviewed date"]
    ];
    return {
      id: "draft-0" + n,
      label: "Draft Record 0" + n,
      status: statusCycle[n - 1],
      missing: missingCycle[n - 1]
    };
  });

  /* ================= DOM HELPERS ================= */

  const $ = function (sel, root) { return (root || document).querySelector(sel); };
  const $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        if (key === "class") node.className = attrs[key];
        else if (key === "text") node.textContent = attrs[key];
        else if (key.indexOf("on") === 0 && typeof attrs[key] === "function") {
          node.addEventListener(key.slice(2).toLowerCase(), attrs[key]);
        } else {
          node.setAttribute(key, attrs[key]);
        }
      });
    }
    (children || []).forEach(function (child) {
      if (child) node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function statusPillClass(status) { return "status-pill status-pill--" + status; }

  /* ================= NAVIGATION ================= */

  const mainEl = $("#main-content");
  const menuToggle = $("#menuToggle");
  const siteNav = $("#siteNav");
  const navScrim = $("#navScrim");

  function routeFromHash() {
    const hash = (window.location.hash || "").replace("#", "");
    return ROUTES.indexOf(hash) !== -1 ? hash : "home";
  }

  function goTo(route, opts) {
    opts = opts || {};
    if (ROUTES.indexOf(route) === -1) route = "home";
    state.route = route;
    if (window.location.hash.replace("#", "") !== route) {
      window.location.hash = route;
    }
    render();
    if (!opts.skipFocus) {
      const heading = $("#view-" + route + " h1");
      if (heading) {
        heading.setAttribute("tabindex", "-1");
        heading.focus({ preventScroll: false });
      }
    }
    closeMobileNav();
  }

  function renderNavigation() {
    $$(".site-nav__link").forEach(function (link) {
      const isCurrent = link.getAttribute("data-route") === state.route;
      if (isCurrent) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    $$(".view").forEach(function (view) {
      view.hidden = view.getAttribute("data-view") !== state.route;
    });
  }

  function openMobileNav() {
    siteNav.classList.add("is-open");
    menuToggle.setAttribute("aria-expanded", "true");
    navScrim.hidden = false;
    navScrim.setAttribute("data-open", "true");
    document.addEventListener("keydown", trapNavEscape);
  }
  function closeMobileNav() {
    siteNav.classList.remove("is-open");
    menuToggle.setAttribute("aria-expanded", "false");
    navScrim.hidden = true;
    navScrim.removeAttribute("data-open");
    document.removeEventListener("keydown", trapNavEscape);
  }
  function trapNavEscape(evt) {
    if (evt.key === "Escape") { closeMobileNav(); menuToggle.focus(); }
  }

  menuToggle.addEventListener("click", function () {
    if (siteNav.classList.contains("is-open")) closeMobileNav();
    else openMobileNav();
  });
  navScrim.addEventListener("click", closeMobileNav);

  document.addEventListener("click", function (evt) {
    const link = evt.target.closest("[data-route]");
    if (link) {
      evt.preventDefault();
      goTo(link.getAttribute("data-route"));
      return;
    }
    const gotoBtn = evt.target.closest("[data-goto]");
    if (gotoBtn) {
      goTo(gotoBtn.getAttribute("data-goto"));
    }
  });

  window.addEventListener("hashchange", function () {
    state.route = routeFromHash();
    render();
  });

  /* ================= RENDER FUNCTIONS ================= */

  function renderDashboard() {
    const grid = $("#metricGrid");
    grid.innerHTML = "";
    DASHBOARD_METRICS.forEach(function (m) {
      grid.appendChild(el("div", { class: "metric-card" }, [
        el("dt", { class: "metric-card__label", text: m.label }),
        el("dd", { class: "metric-card__value", text: m.value })
      ]));
    });
  }

  function renderDraftStatusFilterOptions() {
    const select = $("#draftStatusFilter");
    select.innerHTML = '<option value="">All statuses</option>';
    REVIEW_STATUSES.forEach(function (s) {
      select.appendChild(el("option", { value: s.value, text: s.label }));
    });
  }

  function filteredDrafts() {
    const text = state.draftFilter.text.trim().toLowerCase();
    const status = state.draftFilter.status;
    return draftRecords.filter(function (d) {
      const matchesText = !text || d.label.toLowerCase().indexOf(text) !== -1;
      const matchesStatus = !status || d.status === status;
      return matchesText && matchesStatus;
    });
  }

  function renderDraftList() {
    const list = $("#draftList");
    list.innerHTML = "";
    const drafts = filteredDrafts();
    if (!drafts.length) {
      list.appendChild(el("li", { class: "empty-state", text: "No draft records match this filter." }));
      return;
    }
    drafts.forEach(function (d) {
      const li = el("li", {});
      const btn = el("button", {
        type: "button",
        class: "draft-item",
        "aria-pressed": String(d.id === state.selectedDraftId),
        onClick: function () { selectDraft(d.id); }
      }, [
        el("span", { class: "draft-item__title", text: d.label }),
        el("span", { class: statusPillClass(d.status), text: d.status })
      ]);
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  function selectDraft(id) {
    state.selectedDraftId = id;
    renderDraftList();
    renderDraftDetail();
  }

  function renderDraftDetail() {
    const panel = $("#draftDetail");
    panel.innerHTML = "";
    const draft = draftRecords.find(function (d) { return d.id === state.selectedDraftId; });
    if (!draft) {
      panel.appendChild(el("p", { class: "empty-state", text: "Select a draft record to open its detail panel." }));
      return;
    }

    panel.appendChild(el("h2", { text: draft.label }));
    panel.appendChild(el("span", { class: statusPillClass(draft.status), text: draft.status }));
    panel.appendChild(el("div", { class: "notice notice--warn notice--tight" }, [
      el("strong", { text: "Quarantined draft. " }),
      el("span", { text: "This record is unreviewed and must not be presented as verified legal content." })
    ]));

    panel.appendChild(el("h3", { text: "Missing information checklist" }));
    const checklist = el("ul", { class: "checklist" });
    MISSING_INFO_FIELDS.forEach(function (field) {
      const isMissing = draft.missing.indexOf(field) !== -1;
      checklist.appendChild(el("li", {}, [
        el("span", { text: isMissing ? "☐" : "☑", class: isMissing ? "missing" : "present", "aria-hidden": "true" }),
        el("span", { text: field + (isMissing ? " — missing" : " — recorded") })
      ]));
    });
    panel.appendChild(checklist);

    const actions = el("div", { class: "form-actions" }, [
      el("button", { type: "button", class: "btn btn--ghost", onClick: function () {
        announcePrototypeAction(draft.label, "sent for source linking");
      } }, ["Prototype action: send to source linking"]),
      el("button", { type: "button", class: "btn btn--ghost", onClick: function () {
        announcePrototypeAction(draft.label, "flagged for correction");
      } }, ["Prototype action: flag for correction"])
    ]);
    panel.appendChild(actions);
    panel.appendChild(el("p", { id: "draftActionAnnounce", class: "form-result", "aria-live": "polite" }));
  }

  function announcePrototypeAction(label, verb) {
    const target = $("#draftActionAnnounce");
    if (target) {
      target.setAttribute("data-state", "ok");
      target.textContent = label + " " + verb + " (prototype action — nothing was saved).";
    }
  }

  function initDraftFilters() {
    renderDraftStatusFilterOptions();
    $("#draftTextFilter").addEventListener("input", function (evt) {
      state.draftFilter.text = evt.target.value;
      renderDraftList();
    });
    $("#draftStatusFilter").addEventListener("change", function (evt) {
      state.draftFilter.status = evt.target.value;
      renderDraftList();
    });
  }

  /* ================= REVIEW STATUS HELPERS ================= */

  function populateReviewStatusSelect(select) {
    if (!select) return;
    select.innerHTML = "";
    REVIEW_STATUSES.forEach(function (s) {
      select.appendChild(el("option", { value: s.value, text: s.label }));
    });
  }

  function renderReviewStatusLegend() {
    const list = $("#statusLegend");
    list.innerHTML = "";
    REVIEW_STATUSES.forEach(function (s) {
      list.appendChild(el("li", {}, [
        el("code", { text: s.label }),
        el("span", { class: "status-desc", text: " — " + s.meaning })
      ]));
    });
  }

  /* ================= FORM VALIDATION: SOURCE REGISTRY ================= */

  function isValidUrl(value) {
    try {
      const u = new URL(value);
      return u.protocol === "http:" || u.protocol === "https:";
    } catch (e) {
      return false;
    }
  }

  function isValidSha256(value) {
    return /^[a-f0-9]{64}$/i.test(value);
  }

  function initSourceForm() {
    const form = $("#sourceForm");
    const urlInput = $("#srcUrl");
    const shaInput = $("#srcSha");
    const urlError = $("#srcUrlError");
    const shaError = $("#srcShaError");
    const ownerError = $("#ownerError");
    const result = $("#sourceFormResult");

    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      let valid = true;

      urlError.textContent = "";
      shaError.textContent = "";
      ownerError.textContent = "";
      urlInput.removeAttribute("aria-invalid");
      shaInput.removeAttribute("aria-invalid");

      if (!isValidUrl(urlInput.value.trim())) {
        urlError.textContent = "Enter a valid http(s) source URL.";
        urlInput.setAttribute("aria-invalid", "true");
        valid = false;
      }

      const shaValue = shaInput.value.trim();
      if (shaValue && !isValidSha256(shaValue)) {
        shaError.textContent = "SHA-256 must be exactly 64 hexadecimal characters, or left empty.";
        shaInput.setAttribute("aria-invalid", "true");
        valid = false;
      }

      const owners = $$('input[name="owner"]:checked', form);
      if (owners.length !== 1) {
        ownerError.textContent = owners.length === 0
          ? "Select exactly one content owner."
          : "Select only one content owner — currently " + owners.length + " are selected.";
        valid = false;
      }

      result.setAttribute("data-state", valid ? "ok" : "error");
      result.textContent = valid
        ? "Demonstration valid: exactly one owner (" + owners[0].value + ") and well-formed fields. Nothing was sent anywhere — this is a front-end prototype. The production application enforces this rule in Pydantic and SQLite."
        : "Demonstration found validation problems — see the messages above. Nothing was sent anywhere.";
    });

    form.addEventListener("reset", function () {
      window.setTimeout(function () {
        urlError.textContent = "";
        shaError.textContent = "";
        ownerError.textContent = "";
        result.removeAttribute("data-state");
        result.textContent = "";
      }, 0);
    });

    // Live owner-count feedback as checkboxes change.
    $$('input[name="owner"]', form).forEach(function (box) {
      box.addEventListener("change", function () {
        const owners = $$('input[name="owner"]:checked', form);
        ownerError.textContent = owners.length > 1
          ? "Only one content owner may be selected — currently " + owners.length + " are selected."
          : "";
      });
    });
  }

  /* ================= CASE EDITOR: ROW MANAGEMENT ================= */

  const CASE_TABS = [
    { id: "core", label: "Core details" },
    { id: "parties", label: "Parties" },
    { id: "provisions", label: "Provisions" },
    { id: "issues", label: "Issues" },
    { id: "actions", label: "Actions" }
  ];

  function initCaseTabs() {
    const bar = $("#caseTabbar");
    bar.innerHTML = "";
    CASE_TABS.forEach(function (tab) {
      bar.appendChild(el("button", {
        type: "button",
        class: "tab-btn",
        id: "tab-" + tab.id,
        role: "tab",
        "aria-selected": String(tab.id === state.caseTab),
        "aria-controls": "panel-" + tab.id,
        onClick: function () { setCaseTab(tab.id); }
      }, [tab.label]));
    });
  }

  function setCaseTab(tabId) {
    state.caseTab = tabId;
    $$(".tab-btn").forEach(function (btn) {
      btn.setAttribute("aria-selected", String(btn.id === "tab-" + tabId));
    });
    $$(".case-panel").forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-panel") !== tabId;
    });
  }

  function nextRowId() { return "row-" + (state.rowSeq++); }

  function addCaseRow(kind) {
    const row = { id: nextRowId() };
    if (kind === "parties") { row.name = ""; row.role = ""; }
    if (kind === "provisions") { row.statute = ""; row.section = ""; }
    if (kind === "issues") { row.order = state.caseRows.issues.length + 1; row.text = ""; }
    if (kind === "actions") { row.order = state.caseRows.actions.length + 1; row.text = ""; }
    state.caseRows[kind].push(row);
    renderCaseRows(kind);
    renderCasePreview();
  }

  function removeCaseRow(kind, id) {
    state.caseRows[kind] = state.caseRows[kind].filter(function (r) { return r.id !== id; });
    if (kind === "issues" || kind === "actions") {
      state.caseRows[kind].forEach(function (r, i) { r.order = i + 1; });
    }
    renderCaseRows(kind);
    renderCasePreview();
  }

  function renderCaseRows(kind) {
    const listId = kind === "parties" ? "partiesList"
      : kind === "provisions" ? "provisionsList"
      : kind === "issues" ? "issuesList" : "actionsList";
    const list = $("#" + listId);
    list.innerHTML = "";

    state.caseRows[kind].forEach(function (row) {
      let fields;
      if (kind === "parties") {
        fields = [
          labeledInput("Party name", row.name, function (v) { row.name = v; renderCasePreview(); }, "Instructional placeholder"),
          labeledInput("Role in case", row.role, function (v) { row.role = v; renderCasePreview(); }, "e.g. Sample role")
        ];
      } else if (kind === "provisions") {
        fields = [
          labeledInput("Statute", row.statute, function (v) { row.statute = v; renderCasePreview(); }, "Instructional placeholder"),
          labeledInput("Section", row.section, function (v) { row.section = v; renderCasePreview(); }, "e.g. Sample section")
        ];
      } else {
        fields = [
          labeledInput("Order", String(row.order), function (v) {
            const n = parseInt(v, 10);
            row.order = isNaN(n) ? row.order : n;
            validateOrder(kind);
            renderCasePreview();
          }, "1", "number"),
          labeledInput("Description", row.text, function (v) { row.text = v; renderCasePreview(); }, "Instructional placeholder")
        ];
      }

      const rowEl = el("li", { class: "repeat-row" }, fields.concat([
        el("button", {
          type: "button", class: "btn btn--small btn--danger repeat-row__remove",
          onClick: function () { removeCaseRow(kind, row.id); }
        }, ["Remove"])
      ]));
      list.appendChild(rowEl);
    });

    if (kind === "issues" || kind === "actions") validateOrder(kind);
  }

  function labeledInput(labelText, value, onChange, placeholder, type) {
    const input = el("input", {
      type: type || "text",
      value: value || "",
      placeholder: placeholder || "",
      onInput: function (evt) { onChange(evt.target.value); }
    });
    return el("label", { class: "field" }, [
      el("span", { class: "field__label", text: labelText }),
      input
    ]);
  }

  function validateOrder(kind) {
    const errorId = kind === "issues" ? "#issuesOrderError" : "#actionsOrderError";
    const errorEl = $(errorId);
    const rows = state.caseRows[kind];
    const invalid = rows.some(function (r) { return !r.order || r.order < 1 || isNaN(r.order); });
    const seen = {};
    let duplicate = false;
    rows.forEach(function (r) {
      if (seen[r.order]) duplicate = true;
      seen[r.order] = true;
    });
    if (invalid) {
      errorEl.textContent = "Every " + kind.slice(0, -1) + " needs a positive order number.";
    } else if (duplicate) {
      errorEl.textContent = "Order numbers should be unique for a clear sequence.";
    } else {
      errorEl.textContent = "";
    }
  }

  function initCaseEditor() {
    initCaseTabs();
    setCaseTab("core");
    populateReviewStatusSelect($("#caseReviewStatus"));

    $$('[data-add]').forEach(function (btn) {
      if (btn.closest("#view-case-editor")) {
        btn.addEventListener("click", function () { addCaseRow(btn.getAttribute("data-add")); });
      }
    });

    $$("#panel-core input, #panel-core select, #panel-core textarea").forEach(function (field) {
      field.addEventListener("input", renderCasePreview);
      field.addEventListener("change", renderCasePreview);
    });

    renderCasePreview();
  }

  function renderCasePreview() {
    const body = $("#casePreviewBody");
    body.innerHTML = "";

    const coreFields = [
      ["Slug", $("#caseSlug").value],
      ["Case title", $("#caseTitle").value],
      ["Case number", $("#caseNumber").value],
      ["Citation", $("#caseCitation").value],
      ["Court", $("#caseCourt").value],
      ["Case type", $("#caseType").value],
      ["Decision date", $("#caseDecisionDate").value],
      ["Procedural stage", $("#caseStage").value],
      ["Outcome", $("#caseOutcome").value],
      ["Review status", $("#caseReviewStatus").value],
      ["Last reviewed at", $("#caseLastReviewed").value],
      ["Facts summary", $("#caseFacts").value],
      ["Holding summary", $("#caseHolding").value]
    ];

    const hasAnyContent = coreFields.some(function (f) { return f[1]; }) ||
      state.caseRows.parties.length || state.caseRows.provisions.length ||
      state.caseRows.issues.length || state.caseRows.actions.length;

    if (!hasAnyContent) {
      body.appendChild(el("p", { class: "empty-state", text: "Nothing entered yet. Fill in the fields to see a live preview." }));
      return;
    }

    const dl = el("dl", { class: "preview-dl" });
    coreFields.forEach(function (f) {
      if (!f[1]) return;
      dl.appendChild(el("dt", { text: f[0] }));
      dl.appendChild(el("dd", { text: f[1] }));
    });
    body.appendChild(dl);

    appendPreviewGroup(body, "Parties", state.caseRows.parties.map(function (r) {
      return (r.name || "Unnamed party") + (r.role ? " — " + r.role : "");
    }));
    appendPreviewGroup(body, "Statutory provisions", state.caseRows.provisions.map(function (r) {
      return (r.statute || "Unnamed statute") + (r.section ? " § " + r.section : "");
    }));
    appendPreviewGroup(body, "Ordered issues", state.caseRows.issues
      .slice().sort(function (a, b) { return a.order - b.order; })
      .map(function (r) { return r.order + ". " + (r.text || "—"); }));
    appendPreviewGroup(body, "Ordered actions", state.caseRows.actions
      .slice().sort(function (a, b) { return a.order - b.order; })
      .map(function (r) { return r.order + ". " + (r.text || "—"); }));
  }

  function appendPreviewGroup(body, title, items) {
    if (!items.length) return;
    body.appendChild(el("dt", { class: "preview-group-title", text: title }));
    const ul = el("ul", { class: "preview-list" });
    items.forEach(function (text) { ul.appendChild(el("li", { text: text })); });
    body.appendChild(ul);
  }

  /* ================= COURT LEARNING GROUNDWORK ================= */

  function initCourtLearning() {
    populateReviewStatusSelect($(".role-review-status"));
    populateReviewStatusSelect($(".guide-review-status"));

    $("#courtRoleForm").addEventListener("submit", function (evt) { evt.preventDefault(); });
    $("#workflowGuideForm").addEventListener("submit", function (evt) { evt.preventDefault(); });

    $("#addWorkflowStep").addEventListener("click", function () {
      state.workflowSteps.push({ id: nextRowId(), order: state.workflowSteps.length + 1, text: "" });
      renderWorkflowSteps();
    });
    renderWorkflowSteps();
  }

  function renderWorkflowSteps() {
    const list = $("#workflowStepsList");
    list.innerHTML = "";
    state.workflowSteps.forEach(function (step) {
      const row = el("li", { class: "repeat-row" }, [
        labeledInput("Order", String(step.order), function (v) {
          const n = parseInt(v, 10);
          step.order = isNaN(n) ? step.order : n;
        }, "1", "number"),
        labeledInput("Step description", step.text, function (v) { step.text = v; }, "Instructional placeholder step"),
        el("button", {
          type: "button", class: "btn btn--small btn--danger repeat-row__remove",
          onClick: function () {
            state.workflowSteps = state.workflowSteps.filter(function (s) { return s.id !== step.id; });
            state.workflowSteps.forEach(function (s, i) { s.order = i + 1; });
            renderWorkflowSteps();
          }
        }, ["Remove"])
      ]);
      list.appendChild(row);
    });
  }

  /* ================= SHA-256 DEMONSTRATION ================= */

  function initHashDemo() {
    const input = $("#hashFileInput");
    const resultBox = $("#hashResult");
    const unsupported = $("#hashUnsupported");
    const copyBtn = $("#hashCopyBtn");
    const copyConfirm = $("#hashCopyConfirm");
    const resetBtn = $("#hashResetBtn");
    let currentHash = "";

    const supported = !!(window.crypto && window.crypto.subtle && window.crypto.subtle.digest);
    if (!supported) {
      unsupported.hidden = false;
      input.disabled = true;
      return;
    }

    input.addEventListener("change", function () {
      const file = input.files && input.files[0];
      if (!file) return;
      copyConfirm.textContent = "";
      file.arrayBuffer().then(function (buffer) {
        return window.crypto.subtle.digest("SHA-256", buffer);
      }).then(function (digest) {
        const bytes = Array.from(new Uint8Array(digest));
        currentHash = bytes.map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
        $("#hashFileName").textContent = file.name;
        $("#hashByteSize").textContent = file.size.toLocaleString() + " bytes";
        $("#hashValue").textContent = currentHash;
        resultBox.hidden = false;
      }).catch(function () {
        currentHash = "";
        resultBox.hidden = true;
        unsupported.hidden = false;
        unsupported.querySelector("span").textContent = "The file could not be hashed in this browser.";
      });
    });

    copyBtn.addEventListener("click", function () {
      if (!currentHash) return;
      const done = function () {
        copyConfirm.textContent = "Copied.";
        window.setTimeout(function () { copyConfirm.textContent = ""; }, 2500);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(currentHash).then(done).catch(function () {
          copyConfirm.textContent = "Copy failed — select and copy the hash manually.";
        });
      } else {
        copyConfirm.textContent = "Clipboard unavailable — select and copy the hash manually.";
      }
    });

    resetBtn.addEventListener("click", function () {
      input.value = "";
      currentHash = "";
      resultBox.hidden = true;
      copyConfirm.textContent = "";
    });
  }

  /* ================= DIAGRAM ZOOM + FULL SCREEN ================= */

  function initDiagrams() {
    $$(".diagram-image").forEach(function (img) {
      img.addEventListener("error", function () {
        img.hidden = true;
        img.closest(".diagram-frame").querySelector(".diagram-placeholder").hidden = false;
      });
      img.addEventListener("click", function () {
        const target = img.closest("[data-diagram]").getAttribute("data-diagram");
        openLightbox(target, img.src, img.alt);
      });
    });

    $$("[data-zoom-in]").forEach(function (btn) {
      btn.addEventListener("click", function () { adjustDiagramZoom(btn.getAttribute("data-target"), 0.2); });
    });
    $$("[data-zoom-out]").forEach(function (btn) {
      btn.addEventListener("click", function () { adjustDiagramZoom(btn.getAttribute("data-target"), -0.2); });
    });
    $$("[data-zoom-reset]").forEach(function (btn) {
      btn.addEventListener("click", function () { setDiagramZoom(btn.getAttribute("data-target"), 1); });
    });
    $$("[data-fullscreen]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const target = btn.getAttribute("data-target");
        const img = $('[data-diagram="' + target + '"] .diagram-image');
        openLightbox(target, img.src, img.alt);
      });
    });
  }

  function adjustDiagramZoom(target, delta) {
    const next = Math.min(3, Math.max(0.4, (state.diagramZoom[target] || 1) + delta));
    setDiagramZoom(target, next);
  }
  function setDiagramZoom(target, value) {
    state.diagramZoom[target] = value;
    const img = $('[data-diagram="' + target + '"] .diagram-image');
    if (img) img.style.transform = "scale(" + value + ")";
  }

  const lightbox = $("#lightbox");
  const lightboxImage = $("#lightboxImage");
  let lastFocusedBeforeLightbox = null;

  function openLightbox(target, src, alt) {
    state.lightboxTarget = target;
    state.lightboxZoom = 1;
    lightboxImage.src = src;
    lightboxImage.alt = alt;
    lightboxImage.style.transform = "scale(1)";
    lastFocusedBeforeLightbox = document.activeElement;
    lightbox.hidden = false;
    $("#lightboxClose").focus();
    document.addEventListener("keydown", handleLightboxKeydown);
  }
  function closeLightbox() {
    lightbox.hidden = true;
    document.removeEventListener("keydown", handleLightboxKeydown);
    if (lastFocusedBeforeLightbox) lastFocusedBeforeLightbox.focus();
  }
  function handleLightboxKeydown(evt) {
    if (evt.key === "Escape") { closeLightbox(); return; }
    if (evt.key === "Tab") {
      const focusable = $$("button", lightbox);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (evt.shiftKey && document.activeElement === first) { evt.preventDefault(); last.focus(); }
      else if (!evt.shiftKey && document.activeElement === last) { evt.preventDefault(); first.focus(); }
    }
  }

  function initLightbox() {
    $("#lightboxClose").addEventListener("click", closeLightbox);
    $("#lightboxZoomIn").addEventListener("click", function () { setLightboxZoom(state.lightboxZoom + 0.2); });
    $("#lightboxZoomOut").addEventListener("click", function () { setLightboxZoom(state.lightboxZoom - 0.2); });
    $("#lightboxZoomReset").addEventListener("click", function () { setLightboxZoom(1); });
  }
  function setLightboxZoom(value) {
    state.lightboxZoom = Math.min(4, Math.max(0.4, value));
    lightboxImage.style.transform = "scale(" + state.lightboxZoom + ")";
  }

  /* ================= INITIALIZATION ================= */

  function render() {
    renderNavigation();
  }

  function init() {
    state.route = routeFromHash();

    renderDashboard();
    initDraftFilters();
    renderDraftList();
    renderDraftDetail();

    initSourceForm();

    initCaseEditor();

    initCourtLearning();

    renderReviewStatusLegend();

    initHashDemo();

    initDiagrams();
    initLightbox();

    render();

    if (!window.location.hash) {
      window.history.replaceState(null, "", "#" + state.route);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
