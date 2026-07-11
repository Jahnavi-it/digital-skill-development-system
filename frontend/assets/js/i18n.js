// ------------------------------------------------------------------
// Phase 5 — Multi-language support (English / Telugu / Hindi)
//
// Approach: rather than requiring every page to be rewritten with
// data-i18n attributes, this translates the *shared chrome* that
// appears on every page (sidebar nav, top navbar, logout button) plus
// the common headings/labels on the main pages, by matching the exact
// English text nodes Claude already knows the site uses. This keeps
// the feature genuinely working without a full framework, at the
// cost of only covering navigation + common labels rather than every
// single sentence in the app (documented in the README).
// ------------------------------------------------------------------

(function () {
  const DICT = {
    "Dashboard": { te: "డ్యాష్‌బోర్డ్", hi: "डैशबोर्ड" },
    "Courses": { te: "కోర్సులు", hi: "कोर्स" },
    "Leaderboard": { te: "లీడర్‌బోర్డ్", hi: "लीडरबोर्ड" },
    "Resume Builder": { te: "రెజ్యూమ్ బిల్డర్", hi: "रिज्यूमे बिल्डर" },
    "Mock Interview": { te: "మాక్ ఇంటర్వ్యూ", hi: "मॉक इंटरव्यू" },
    "Coding Compiler": { te: "కోడింగ్ కంపైలర్", hi: "कोडिंग कंपाइलर" },
    "Internships": { te: "ఇంటర్న్‌షిప్‌లు", hi: "इंटर्नशिप" },
    "Forum": { te: "ఫోరమ్", hi: "फोरम" },
    "Chat": { te: "చాట్", hi: "चैट" },
    "Notifications": { te: "నోటిఫికేషన్‌లు", hi: "सूचनाएं" },
    "Live Classes": { te: "లైవ్ క్లాసులు", hi: "लाइव क्लासेस" },
    "Log out": { te: "లాగ్ అవుట్", hi: "लॉग आउट" },
    "Home": { te: "హోమ్", hi: "होम" },
    "Log in": { te: "లాగిన్", hi: "लॉग इन" },
    "Get started": { te: "ప్రారంభించండి", hi: "शुरू करें" },
    "Welcome back": { te: "తిరిగి స్వాగతం", hi: "वापसी पर स्वागत है" },
    "Course catalog": { te: "కోర్సు జాబితా", hi: "कोर्स सूची" },
    "Find your next skill": { te: "మీ తదుపరి నైపుణ్యాన్ని కనుగొనండి", hi: "अपना अगला कौशल खोजें" },
    "Continue learning": { te: "నేర్చుకోవడం కొనసాగించండి", hi: "सीखना जारी रखें" },
    "Your badges": { te: "మీ బ్యాడ్జీలు", hi: "आपके बैज" },
    "Browse courses": { te: "కోర్సులను చూడండి", hi: "कोर्स ब्राउज़ करें" },
    "In progress": { te: "పురోగతిలో ఉంది", hi: "प्रगति में" },
    "Achievements": { te: "సాధనలు", hi: "उपलब्धियां" },
    "Loading…": { te: "లోడ్ అవుతోంది…", hi: "लोड हो रहा है…" },
  };

  const LANG_NAMES = { en: "English", te: "తెలుగు", hi: "हिंदी" };

  function getLang() {
    return localStorage.getItem("dsds_lang") || (window.Auth && Auth.getUser() && Auth.getUser().language_pref) || "en";
  }

  function setLang(lang) {
    localStorage.setItem("dsds_lang", lang);
    if (window.Auth && Auth.isLoggedIn()) {
      apiRequest("/auth/language", { method: "PUT", auth: true, body: { language_pref: lang } }).catch(() => {});
    }
    applyTranslations(lang);
  }

  // Splits a nav-link's leading emoji (if any) from the text so we can
  // translate just the label and keep the icon, e.g. "📊 Dashboard".
  function translateNode(node, lang) {
    if (!node.dataset.dsdsOriginal) {
      node.dataset.dsdsOriginal = node.textContent;
    }
    const original = node.dataset.dsdsOriginal.trim();
    const emojiMatch = original.match(/^(\p{Emoji_Presentation}|\p{Extended_Pictographic})\s*/u);
    const prefix = emojiMatch ? emojiMatch[0] : "";
    const label = emojiMatch ? original.slice(emojiMatch[0].length) : original;

    const entry = DICT[label];
    if (!entry) return;

    node.textContent = lang === "en" ? original : prefix + (entry[lang] || label);
  }

  function applyTranslations(lang) {
    document.documentElement.lang = lang;
    const selectors = "aside.sidebar nav a, .sidebar .logout, .navbar nav a, h2, h3, p.sub, .eyebrow, button, .empty-state";
    document.querySelectorAll(selectors).forEach((node) => {
      // Only touch leaf-ish elements whose full text is a known label —
      // avoids mangling elements that contain nested markup/child stats.
      if (node.children.length === 0 && node.textContent.trim()) {
        translateNode(node, lang);
      }
    });
  }

  function injectSwitcher() {
    if (document.getElementById("dsds-lang-switch")) return;

    const select = document.createElement("select");
    Object.entries(LANG_NAMES).forEach(([code, label]) => {
      const opt = document.createElement("option");
      opt.value = code;
      opt.textContent = label;
      select.appendChild(opt);
    });
    select.value = getLang();
    select.addEventListener("change", () => setLang(select.value));

    const wrap = document.createElement("div");
    wrap.id = "dsds-lang-switch";
    wrap.appendChild(select);

    const sidebar = document.querySelector("aside.sidebar");
    const navbarNav = document.querySelector(".navbar nav");
    if (sidebar) {
      const logout = sidebar.querySelector(".logout");
      sidebar.insertBefore(wrap, logout || null);
    } else if (navbarNav) {
      navbarNav.insertBefore(wrap, navbarNav.firstChild);
    } else {
      document.body.appendChild(wrap);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    injectSwitcher();
    applyTranslations(getLang());
  });
})();
